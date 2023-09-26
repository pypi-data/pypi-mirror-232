#!/usr/bin/env python
import numpy as np
import math
import sls
import os
import re 
import yaml
import sys
import getopt
import shutil
import transit as tr
from scipy.stats import chi2
from packaging.version import parse as parse_version
import spotintime

'''

PSLS : PLATO Solar-like Light-curve Simulator

If you use PSLS in your research work, please make a citation to Samadi et al (2019, A&A, 624, 117, https://www.aanda.org/articles/aa/abs/2019/04/aa34822-18/aa34822-18.html)
and Marchiori et al (2019, A&A, 627, A71, https://www.aanda.org/articles/aa/abs/2019/07/aa35269-19/aa35269-19.html)

Copyright (c) October 2017, R. Samadi (LESIA - Observatoire de Paris)

This is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this code.  If not, see <http://www.gnu.org/licenses/>.

'''


__version__ = 1.6

jupiterRadius = 71492.0  # km
ua2Km = 149.59e6  # km
# NSR values computed by V. Marchiori (see Marchiori et al 2019, A&A)
NSR_Pmag = np.array([7.76,8.16,8.66,9.16,9.66,10.16,10.66,11.16,11.66,12.16,12.56,12.76,13.16,13.66,14.16,14.66,15.16,15.56])# P magnitude
NSR_Vmag = NSR_Pmag + 0.34 # V magnitude
NSR_values_24 = np.array([10.6,12.9,16.4,20.8,26.7,34.5,44.8,59.2,79.1,106.8,138.5,156.8,205.8,298.6,442.9,668.8,1018.9,1444.4])
NSR_values = NSR_values_24*math.sqrt(24.)

def VmP(teff): 
    '''
	Given the star Teff, return V-P according to Eq. 8 in  Marchiori et al (2019)
	'''
    # return -1.238e-12*teff**3 + 4.698e-8*teff**2 - 5.982e-4*teff + 2.506 # non-compliant with  Marchiori et al (2019)
    return -1.184e-12*teff**3 + 4.526e-8*teff**2 - 5.805e-4*teff + 2.449  # compliant  with  Marchiori et al (2019)

def generateZ(orbitalPeriodSecond, planetSemiMajorAxis,
                  starRadius, SamplingTime, IntegrationTime, TimeShift, sampleNumber,
                  orbitalStartAngleRad, p):
    '''
    :INPUTS:
    orbitalPeriodSecond = orbital period of the planet in second
    planetSemiMajorAxis = semi Major axis in km
    starRadius = star radius in km
    SamplingTime:int = Sampling time in second, (Plato = 25s)
    IntegrationTime : integration time in seconds
    TimeShift: time shift in seconds
    sampleNumber = number of sample we want (==> z.size)
    orbitalStartAngleRad = orbital angle in radians where to start planet position
    p = rp / r*
    :OUTPUTS:
    z = d / r*, is the normalized separation of the centers (sequence of positional offset values)

    E. Grolleau
    L.C. Smith (for the vectorized version, 13.04.2021)
    '''
    angleIncrement = SamplingTime * 2.0 * math.pi / orbitalPeriodSecond
    angle0 = orbitalStartAngleRad + (IntegrationTime/2. + TimeShift)* 2.0 * math.pi / orbitalPeriodSecond
    angles = angleIncrement * np.arange(sampleNumber) +  angle0
    # For occultquad computation we need that z < p+1
    time = np.arange(sampleNumber) * SamplingTime + IntegrationTime/2. + TimeShift
    z = np.where(
        np.sin(angles)>0,
        np.abs((planetSemiMajorAxis / starRadius) * np.cos(angles)),
        p+1
    )
    z = z.clip(min=0, max=p+1)
    return (time, z)


def psd (s,dt=1.):
    '''
 Inputs:
 s : signal (regularly sampled)
 dt: sampling (seconds)

 Outputs:
 a tuple (nu,psd)
 nu: frequencies (Hz)
 psd: power spectral density  (in Hz^-1). A double-sided PSD is assumed
    '''
    
    ft=np.fft.fft(s)
    n=len(s)
    ps=(np.abs(ft))**2*(dt/n)
    nu=np.fft.fftfreq(n,d=dt)
    nnu=n//2
    return (nu[0:nnu],ps[0:nnu])


def platotemplate(duration,dt=1.,V=11.,n=24,residual_only=False,cl=None):
    '''

 Return the total noise budget (in  ppm^2/ Hz) as a function of frequency.
 The budged includes all the random noise (including the  photon noise) and the resdiual error (after all corrections)
 It is assumed that the residual error is not correlated among the telescopes
 
 Inputs:
 duration : in days
 dt :sampling time i seconds
 V : star magnitude
 n : number of telescope (default: 24)
 
 Outputs:
 a tuple (nu,psd)
 nu: frequencies (Hz)
 psd: power spectral density  (in ppm^2 / Hz)

 cl: confidence level (<1), if specified the mean white noise level is multiplied by the threshold corresponding to the given confidence level, ,if not specified (None) the function returns the mean noise level
 '''
    V0 = 11 # reference magnitude
    scl = (24./n) # we assume that all the noises including the residual error are not correlated over the telescopes
    sclpn = 10.**( (V-V0)/2.5 ) # scaling applied on the random noise only
    if(cl!=None):
        threshold = chi2.ppf(cl,2)/chi2.mean(2) # 2 is the degree of freedom
        sclpn *= threshold
    n=int(np.ceil(86400.*duration/dt) )
    nu=np.fft.fftfreq(n,d=dt)
    m = int(n/2.)
    nu=nu[0:m]
    nu0=20e-6 # R-SCI-350, R-SCI-342 
    nu1=3e-6 #  R-SCI-350, R-SCI-342 
    s0 = 0.68 * 1e3 # R-SCI-342 
    s1 = 50.*1e3  #  R-SCI-350
    s3 = 3.0 * 1e3  # [ppm/Hz^(1/2)] random noise level at V=11 for 24 telescopes (equivalent to 50 ppm/hr)

    ps=np.zeros(m)
    j=np.where( nu >= nu0)
    if( j != -1):
        ps[j[0]] = (s0**2 + s3**2*sclpn*(residual_only==False))*scl
    j=np.where( (nu < nu0) & (nu>0.) )
    if( j != -1):
        ps[j[0]] = (np.exp( np.log(s1) + (np.log(s0)-np.log(s1)) * ((np.log(nu[j])-np.log(nu1))/(np.log(nu0)-np.log(nu1)) ))**2  + s3**2*sclpn*(residual_only==False))*scl
    return (nu,ps)
    

def pip(x,y,poly):
    '''
    test if a point is inside a polygon
    
    Taken from: http://geospatialpython.com/2011/01/point-in-polygon.html
    
    '''
    n = len(poly)
    inside = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside


def rebin1d(array,n):
    nr=int(float(array.shape[0])/float(n))
    return (np.reshape(array,(n,nr))).sum(1)
 
def search_model(ModelDir,ES,logg,teff,  dlogg=0.01,dteff=15.,verbose=False,plot=False):
    
    pack = np.load(ModelDir+'data.npz')
    files = pack['files']     
    glob = pack['glob'] # star global parameters
    ## references = pack['references'] # references (&constants) parameters
    
    if(ES.lower() == 'any'):
        sel = np.ones(glob.shape[0],dtype=np.bool)
    elif(ES.lower() == 'ms'):
        sel = (glob[:,28] > 1e-3)
    elif(ES.lower() == 'sg'):
        sel = (glob[:,28] <= 1e-3) & (glob[:,20] < 200.) 
    else:
        raise sls.SLSError("unmanaged evolutionary status:"+ ES)
    
    if(sel.sum()==0):
        raise sls.SLSError("no models full fill the criteria ")
    
    glob = glob[sel,:]
    files = files[sel]
    Chi2 = ((glob[:,17]-teff)/dteff)**2 +  ((glob[:,18]-logg)/dlogg)**2
    
    i = np.argmin(Chi2)
    teffb = glob[i,17]
    loggb = glob[i,18]
    filename = files[i]
    if(type(filename) == bytes or type(filename) == np.bytes_): # solve a compatibility issue with strings coded as bytes
        filename = filename.decode()
    name = re.sub('-[n]ad\.osc','',os.path.basename(filename))
    
    if(verbose):        
        print(('Best matching, teff = %f ,logg = %f, Chi2 = %f') % (teffb, loggb,Chi2[i]))   
        print(('Star model name: %s') % (name))
        
    if(plot):
        plt.figure(200)
        plt.clf()
        plt.plot(glob[:,17],glob[:,18],'k+')
        plt.plot([teffb],[loggb],'ro')
        plt.gca().invert_yaxis()
        plt.gca().invert_xaxis()
        plt.ylabel(r'$log g$')
        plt.xlabel(r'$T_{\rm eff}$ [K]')
        plt.draw()
        
    return   name  , teffb , loggb
    
    '''
    files = pack['files']     
    glob = pack['glob'] # star global parameters
    
    
    glob[i,j],
    i: model index
    j: parameter index:
      0 : M_star
      1 : R_tot
      2 : L_tot
      3 : Z0
      4 : X0
      5 : alpha
      6 : X in CZ
      7 : Y in CZ
      8 : d2p
      9 : d2ro
      10 : age
      11 : wrot initial (global rotation velocity)
      12 : w_rot initial
      13 : g constante de la gravitaion
      14 : msun
      15 : rsun
      16 : lsol
      17 : Teff
      18 : log g
      19 : Tc temperature at the center
      20 : numax (scaling) [muHz]
      21 : deltanu (scaling) [muHz]
      22 : acoustic diameter [sec]
      23 : nuc, cutoff frequency, at the photosphere [muHz]
      24 : nuc, cutoff frequency, at the r=rmax [muHz]
      25 : deltaPI_1 [sec]
      26,27 : r1,r2 -> interval in radii on which the Brunt-Vaisala is integrated for the calculation of deltaPI
      28 : Xc
      29 : Yc
      30 : acoustic diameter [sec], computed on the basis of the .amdl file (can be oversampled)
      31 : acoustic depth of the Gamma1 bump associated with the first He ionization zone
      32 : acoustic depth of the Gamma1 bump associated with the second He ionization zone
      33 : acoustic depth of the base of the convective zone    

    references[i]: some references values:
            0: msun
            1: rsun
            2: lsun
            3: teff sun
            4: logg sun
            5: numax ref. (Mosser et al 2013)
            6: deltanu ref. (Mosser et al 2013)
            7: nuc sun (Jimenez 2006)
    '''

def prepare_spot_parameters(Star,Spot,Duration,seed=None,verbose=False):
    # gather together all the parameters used by the spot modelling library (spotintime)


    # mean rotation period in days
    prot =  Star['SurfaceRotationPeriod']
    if(prot<=0):
        raise sls.SLSError("surface rotation cannot be zero or negative")

    # light curve offset -> ??
    c0 = 0.0

    # inclination of the star in degrees, default value: 90
    incl = Star['Inclination']
    if(incl<=0):
        print('WARNING: inclination angle is zero, no spot signature possible!')

    # differential rotation (dimensionless), default value: 0
    domega = Spot['dOmega']

    #spots radii in degrees , default value: 2.5
    rayi = Spot['Radius']
    nspots = len(rayi)

    #spots latitudes in degrees
    lati =  Spot['Latitude']

    #spots longitudes in degrees, default value: 0
    longi = Spot['Longitude']

    # lifetime of the spot in days, default value: infinity
    taui = np.empty(nspots, dtype=object)
    for i in range(nspots):
        if( not isinstance(Spot['Lifetime'][i], str)):
            # if( Spot['Lifetime'][i].lowercase() != 'infinity'  ):
            taui[i] = Spot['Lifetime'][i]

    #time of maximum flux contrast of the spot in days, default value: 0
    ti0 = Spot['TimeMax']
    np.random.seed(seed)
    for i in range(nspots):
        if( ti0[i] <0):
            ti0[i] = np.random.random()*(Duration+4*taui[i]) -2*taui[i]
            if(verbose):
                print('TimeMax for spot #%i is drawn randomly and take the value: %f days' % (i,ti0[i]))
            # print(ti0[i],taui[i])

    #flux of the spot in units of unspotted stellar flux  (maximum constrast of the spot), default value: 0.7
    fsi =  Spot['Contrast']

    #limb darkening coefficient of the star, default: 0.59
    mue = Spot['MuStar']

    #limb darkening coefficient of the spot, default:   0.78
    mus = Spot['MuSpot']

    params = np.empty(int(7 + 6 * nspots), dtype=object)
    params[0] = nspots
    params[1] = np.log(prot)
    params[2] = incl
    params[3] = domega
    params[4: 4 + nspots] = rayi
    params[4 + nspots:4 + 2 * nspots] = lati
    params[4 + 2 * nspots:4 + 3 * nspots] = longi
    params[4 + 3 * nspots:4 + 4 * nspots] = ti0
    params[4 + 4 * nspots:4 + 5 * nspots] = taui/prot # -> in unit of rotation period
    params[4 + 5 * nspots:4 + 6 * nspots] = fsi
    params[4 + 6 * nspots] = c0
    params[5 + 6 * nspots] = mue
    params[6 + 6 * nspots] = mus

    return params

def generate_spot_LC(params,Sampling,Duration,TimeShift):
    # cadence = Instrument['Sampling']  # cadence in seconds

    # the spot Lightcurve (LC) is modelled at a cadence shorter than the rotation period but in general at a longer than the working cadence
    # then the short cadence LC (PSLS working cadence) is obtained by interpolating the long cadence LC
    prot = math.exp(params[1])

    # cadence used for the spot modelling (in days)
    cadence_lc = prot/100.  # in days

    # number of points in the long cadence  light curve
    n_lc  = int( math.ceil(Duration/cadence_lc) )

    # time in days (for the long cadence LC)
    t_lc = np.arange(n_lc)*cadence_lc

    nspots = int(params[0])

    # computes long cadence   light curve and returns in flx
    [flx_lc, inispots, ovl] = spotintime.paramtolc(params, t_lc, nspots)

    if ovl == 1:
        raise sls.SLSError("spot-Light curve not created because overlapping spots, please reconsider the spot parameters")

    # interpolate the spot model at the working cadence
    n =  int(Duration*86400./Sampling)
    t = (np.arange(n)*Sampling+ TimeShift)/86400.
    flx = np.interp(t,t_lc,flx_lc)

    # plt.figure(110)
    # plt.clf()
    # plt.plot(t,flx)
    # plt.draw()
    # plt.show()


    return flx


def usage():
    print ("usage: psls.py config.yaml")
    print ("      : ")
    print ("Options:")
    print ("-v : print program version")
    print ("-h : print this help")
    print ("-P : do some plots")
    print ("--pdf : the plots are saved as PDF otherwise as PNG (default)")
    print ("-V : verbose mode")
    print ("-f : save the LC associated with each individual camera, otherwise average over all the cameras (this is the default choice)")
    print ("-m : save the merged LC: LC from the same group of camera are averaged and then averaged LC are merged(/interlaced)")
    print ("-o <path> : output directory (the working directory is by default assumed)")
    print ("-M <number> : number of Monte-Carlo simulations performed (not yet operational)")
    print ("--extended-plots : an extended set of plots are displayed (activates automatically  the -P option)")
    



if(len(sys.argv)<2):
    usage()
    sys.exit(2)
try:
    opts,args = getopt.getopt(sys.argv[1:],"hvPVo:fmM:",["pdf","extended-plots"])

except getopt.GetoptError as err:
    print (str(err))
    usage()
    sys.exit(2)

Verbose = False
Plot = False
OutDir = '.'
FullOutput =  False  # single camera light-curves are saved 
MergedOutput = False  # LC from the same group of camera are averaged and  then averaged LC are merged(/interlaced)
Pdf = False
MC = False  # Monte-Carlo simulations on/off 
nMC = 1 # Number of  Monte-Carlo simulations
ExtendedPlots = False
for o, a in opts:
    if o == "-h" :
        usage()
        sys.exit(1)
    elif o == "-v":
        print (__version__)
        sys.exit(1)
    elif o == "-V":
        Verbose = True
    elif o == "-P":
        Plot = True
    elif o == "-f":
        FullOutput = True
    elif o == "-m":
        MergedOutput = True
    elif o == "-o":
        OutDir = a
    elif o == "-M":
        MC = True
        nMC = int(a)
    elif o == "--pdf":
            Pdf = True    
    elif o == "--extended-plots":
        ExtendedPlots = True
        Plot = True
    else:
        print ("unhandled option %s" % (o))
        sys.exit(1)


nargs = len(args)
if nargs > 1 :
    print ("too many arguments")
    usage()
    sys.exit()

if nargs < 1 :
    print ("missing arguments")
    usage()
    sys.exit()

if(MC & Plot):
    print ("The options -M and -P are not compatible. ")    
    sys.exit()

if(MC & Verbose):
    print ("The options -M and -V are not compatible. ")    
    sys.exit()

if(Plot):   
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    plt.ion()

if (FullOutput & MergedOutput):
    print ("The options -m and -f are not compatible. ")
    sys.exit()
  

config=args[0]

stream = open(config, 'r')    # 'document.yaml' contains a single YAML document.
if(parse_version(yaml.__version__)< parse_version("5.0")):
    cfg = yaml.load(stream)
else:
    cfg = yaml.load(stream, Loader=yaml.FullLoader)
stream.close()

OutDir = os.path.normpath(OutDir) + '/'

Star = cfg['Star'] 
StarModelType = Star['ModelType']
StarModelName = Star['ModelName']

Osc = cfg['Oscillations']
OscEnable = Osc['Enable'] 

StarID = Star['ID']
StarName = ("%10.10i") % StarID
StarTeff,StarLogg = Star['Teff'],Star['Logg']
StarES = Star['ES']
if(Verbose):
    print ('Star name: ' + StarName)

UP = StarModelType.lower() == 'up'

if (UP):
    DPI = Osc['DPI']
    q = Osc['q']
    numax = Osc['numax']
    delta_nu =  Osc['delta_nu']    
else:
    sls.numaxref= 3050.
    StarModelDir = Star['ModelDir']
    if(StarModelDir is None):
        StarModelDir = '.'
    StarModelDir = os.path.normpath(StarModelDir) + '/'
    if ( (StarModelType.lower() == 'text') ):
        StarFreqFile = StarModelDir +  StarModelName
        StarFreqFileType = 0
        numax = Osc['numax']
        delta_nu =  Osc['delta_nu']
    elif ( (StarModelType.lower() == 'single') or (StarModelType.lower() == 'adipls') ):
        _, extension = os.path.splitext(StarModelName)
        if(extension==''):
            StarFreqFile = StarModelDir + StarModelName + '.gsm'
        else:
            StarFreqFile = StarModelDir + StarModelName
        StarFreqFileType = 1
        numax = -1.
        delta_nu = -1.
    elif(StarModelType.lower() == 'grid'):
        StarFreqFileType = 1
        numax = -1.
        delta_nu = -1.
        if(Verbose):
            print ('requested values:')
            print (('teff = %f ,log g = %f') % (StarTeff, StarLogg))   
        StarModelName,StarTeff,StarLogg = search_model(StarModelDir,StarES,StarLogg,StarTeff,verbose=Verbose,plot=Plot)
        if(Verbose):
            print ('closest values found:')
            print (('teff = %f ,log g = %f') % (StarTeff, StarLogg))   
        StarFreqFile = StarModelDir + StarModelName + '.gsm'
    else:
        print ("unhandled StarModelType: %s" % (StarModelType))
        sys.exit(1)

    logTeff = math.log10(StarTeff)
    SurfaceEffects = Osc['SurfaceEffects']
    if(SurfaceEffects and (StarFreqFileType>0)):
        
        if(  pip(StarTeff,StarLogg,[[5700.,4.6],[6700.,4.4],[6500.,3.9],[5700,3.9]]) == False):
            print ("surface effects: Teff and log g outside the table") 
            sys.exit(1) 

        # from Sonoi et al 2015, A&A, 583, 112  (Eq. 10 & 11)
        logma =  7.69 * logTeff -0.629 * StarLogg -28.5
        logb = -3.86*logTeff  + 0.235 * StarLogg + 14.2
    
        a =  - 10.**logma
        b = 10.**logb
        if(Verbose):
            print (('Surface effects parameters, a = %f ,b = %f') %  (a,b))
    
    else:
        a = 0.
        b = 1.


OutDir = os.path.normpath(OutDir) + '/'

Granulation = cfg['Granulation']

Transit = cfg['Transit']

Observation = cfg['Observation']
Instrument = cfg['Instrument']
IntegrationTime = Instrument['IntegrationTime']

# initialization of the state of the RNG
MasterSeed = Observation['MasterSeed']
NGroup = Instrument['NGroup']
NCamera = Instrument['NCamera']  # Number of camera per group (1->6)

np.random.seed(MasterSeed)
seeds = np.random.randint(0, 1073741824 + 2,size=NGroup*NCamera+10)
if(Star['Seed']>0):
    seeds[0] = int(Star['Seed']) # seed not controlled by the master seed

Sampling,Duration,StarVMag = Instrument['Sampling'],Observation['Duration'],Star['Mag']

StarPMag = StarVMag - VmP(StarTeff)
StarVpMag = StarPMag + 0.34 # PLATO V reference magnitude (reference star of 6000K)

activity = None
Activity = cfg['Activity']
if(Activity['Enable']):
    activity = (Activity['Sigma'],Activity['Tau'])

spot = None
Spot = Activity['Spot']
if(Spot['Enable']):
    if(Spot['Seed']>0):
        seeds[2] = int(Spot['Seed'])
    spot = prepare_spot_parameters(Star,Spot,Duration,seed=seeds[2],verbose=Verbose)


if(Verbose):
    print ('V magnitude: %f' % StarVMag)
    print ('P magnitude: %f' % StarPMag)
    print ('Reference V PLATO magnitude (6000 K): %f' % StarVpMag)

if (UP):
    # Simulated stellar signal, noise free (nf), UP
    time,ts,f,ps,mps_nf,opar,_ =  sls.gen_up(StarID, numax,Sampling,Duration, 
                                             StarVMag,delta_nu =  delta_nu, mass = -1. , seed =seeds[0] , pn_ref = 0.,  wn_ref= 0., mag_ref = 6.,verbose = Verbose, teff = StarTeff, DPI = DPI,  q = q , GST = 1 , incl = Star['Inclination'] , rot_f = Star['CoreRotationFreq'] , path = OutDir  , granulation = (Granulation['Enable'] == 1)  , oscillation = OscEnable)

else:
    # Simulated stellar signal, noise free
    time,ts,f,_,mps_nf,opar,_ = sls.gen_osc_spectrum(StarID,StarFreqFile,StarTeff,Sampling,Duration,StarVMag,verbose=Verbose,seed=seeds[0],
                                            mag_ref=StarVMag,pn_ref= 0.,wn_ref= 0., a=a,b=b,plot=0, rot_period_sur =  Star['SurfaceRotationPeriod'] , 
                                            incl = Star['Inclination'] , activity = activity, granulation=Granulation['Enable'], path = OutDir , oscillation = OscEnable,
                                                      type = StarFreqFileType,numax=numax,deltanu=delta_nu)


if(Transit['Enable']):
    SampleNumber = time.size
    StarRadius = opar[0]['radius']*sls.rsun*1e-5 # in km
    PlanetRadius = Transit['PlanetRadius'] * jupiterRadius  # in km
    p = PlanetRadius / StarRadius
    _, z = generateZ(Transit['OrbitalPeriod']*86400., Transit['PlanetSemiMajorAxis']*ua2Km,
              StarRadius,Sampling, IntegrationTime, 0. , SampleNumber,
              Transit['OrbitalAngle']*math.pi/180., p)
    ## gamma = [.25, .75]
    gamma = np.array(Transit['LimbDarkeningCoefficients'],dtype=np.float64)
    transit = tr.occultquad(z, p, gamma, verbose=Verbose)
    if(Verbose):
        print (('Star radius [solar unit]: %f') % ( opar[0]['radius'])) 
        print ("Planet Radius/ Star Radius = {0:}".format(p))
        print (("Transit depth: %e" ) % (np.max(transit)/np.min(transit)-1.))
    if(Plot):
        plt.figure(110)
        plt.clf()
        plt.title(StarName+ ', transit')
        plt.plot(time/86400.,(transit-1.)*100.)
        plt.ylabel('Flux variation [%]')
        plt.xlabel('Time [days]')
        plt.draw()

        # plt.figure(111)
        # plt.clf()
        # plt.title(StarName+ ', transit')
        # plt.plot(time/86400.,z)
        # plt.xlabel('Time [days]')
        # plt.draw()
        # plt.show(block=True)

Systematics = Instrument['Systematics']
SystematicDataVersion = int(Systematics['Version'])
DataSystematic = None
if (Systematics['Enable']):
    if(Systematics['Seed']>0): # seed NOT controlled by the master seed
        seeds[1] = int(Systematics['Seed'])
    if(SystematicDataVersion>0):
        DriftLevel = (Systematics['DriftLevel']).lower() 
    else:
        DriftLevel = None
    DataSystematic = sls.ExtractSystematicDataMagRange(
        Systematics['Table'],StarVpMag,version=SystematicDataVersion,DriftLevel=DriftLevel,
        Verbose=Verbose,seed=seeds[1])
    
# Total white-noise level ppm/Hz^(1/2), for a each single Camera
RandomNoise =  Instrument['RandomNoise']
if RandomNoise['Enable']:
    if (RandomNoise['Type'].lower() == 'user'):
        NSR = float(RandomNoise['NSR'])
    elif (RandomNoise['Type'].lower() == 'plato_scaling'):
        if( (StarPMag<NSR_Pmag[0]-0.25) or (StarPMag>NSR_Pmag[-1]+0.25) ):
            print ("Warning: Star magnitude out of range, boundary NSR value is assumed")
        NSR = np.interp(StarPMag, NSR_Pmag, NSR_values, left=NSR_values[0], right=NSR_values[-1])
    elif (RandomNoise['Type'].lower() == 'plato_simu'):
        if(DataSystematic is None):
            raise sls.SLSError("RandomNoise: when Type=PLATO_SIMU, systematic errors must also be activated")   
        if(SystematicDataVersion<1):
            raise sls.SLSError("RandomNoise: when Type=PLATO_SIMU, data version for systematic errors must be >0")   
        NSR = -1.
    else:
        raise sls.SLSError("unknown RandomNoise type: "+ RandomNoise['Type'] + ' Can be either USER, PLATO_SCALING or PLATO_SYSTEMATICS')        
else:
    NSR = 0.
W =  NSR*math.sqrt(3600.) # ppm/Hr^(1/2) -> ppm/Hz^(1/2)
opar[1]['white_noise'] = W #  ppm/Hz^(1/2)
dt = opar[1]['sampling'] 
nyq = opar[1]['nyquist']
if(Verbose and W>=0.):
        print ('NSR for one camera: %f [ppm.sqrt(hour)]' % NSR)
        print ('Total white-noise for one Camera [ppm/Hz^(1/2)]: %f' % W)
        print ('Total white-noise at sampling time [ppm]: %f' % (W/math.sqrt(Sampling)))
if(Verbose):
        print ('Nyquist frequency [muHz]: %f' % nyq)
        print ('frequency resolution [muHz]: %f' % f[0])

TimeShift = Instrument['TimeShift']
       

nt = time.size
full_ts = np.zeros((nt,NGroup,NCamera,5))
nu = np.fft.fftfreq(nt,d=dt)[0:nt//2] * 1e6 # frequencies, muHz
nnu = nu.size
spec = np.zeros((NGroup,nu.size))
dnu = nu[1]

full_ts_SC = np.zeros((nt,NGroup,NCamera)) # systematic error only

for iMC in range(nMC):
    for i in range(NGroup):
        if(Verbose):
            print (('Group: %i') % (i))
        # simulating stellar signal
        time_i, ts_i , ps_i, _ =  sls.mpsd2rts(f*1e-6,mps_nf*1e6,seed=seeds[0],time_shift=i*TimeShift)
        for j in range(NCamera): 
            full_ts[:,i,j,0] = time_i +  IntegrationTime/2.    
            ts = (1. + ts_i*1e-6  )
            tsSC = 1.
            cumul = 0.
            np.random.seed(seeds[i*NCamera+j+10])
            if(DataSystematic is not None):
                # adding systematic errors
                if(Verbose):
                    print('Generating systematic errors for camera %i of group %i' % (j,i))
                resLC,rawLCvar,_,_, flag= sls.SimSystematicError(Sampling,nt,DataSystematic,i*NCamera+j,seed=seeds[i*NCamera+j+10],version=SystematicDataVersion,Verbose=False)
                if(Verbose):
                    p2p = (np.max(resLC)/np.min(resLC)-1.)*100
                    print('      peak to peak variation [%%]: %f ' %p2p)
                    print('      number of mask updates: %i' % (np.sum(flag)-1))
                full_ts[:,i,j,4] = flag
                cumul += (resLC-1.) 
                tsSC *=  resLC
            else:
                rawLCvar = 1.
            if(W>0.):
                # adding random noise
                cumul += np.random.normal(0.,W*1e-6/math.sqrt(Sampling),size=nt) 
            if(W<0.):
                # adding random noise from LC variance
                cumul += np.random.normal(0.,1.,size=nt)*np.sqrt(rawLCvar)
            ts *= (1. + cumul)        
            if(Transit['Enable']):
                p = PlanetRadius / StarRadius
                _, z = generateZ(Transit['OrbitalPeriod']*86400., Transit['PlanetSemiMajorAxis']*ua2Km,
                                 StarRadius,Sampling, IntegrationTime, i*TimeShift , SampleNumber,
                      Transit['OrbitalAngle']*math.pi/180.,p )
                ## gamma = [.25, .75]
                ts *= tr.occultquad(z, p, gamma, verbose=Verbose)
            if(spot is not None):
                ts *= generate_spot_LC(spot,Sampling,Duration,i*TimeShift)

            # relative flux variation, in ppm
            ts = (ts/np.mean(ts) - 1.)*1e6
            full_ts[:,i,j,1] = ts
            full_ts[:,i,j,2] = i+1 # group number 
            full_ts[:,i,j,3] = j+1 # camera number (within a given group)
            full_ts_SC[:,i,j] = (tsSC/np.mean(tsSC)-1.)*1e6
    
    # LC averaged over the camera groups 
    single_ts = np.zeros((nt,3))
    single_ts[:,0] = np.sum(full_ts[:,:,:,0],axis=(1,2))/float(NGroup*NCamera)
    single_ts[:,1] = np.sum(full_ts[:,:,:,1],axis=(1,2))/float(NGroup*NCamera)
    single_ts[:,2] = np.sum(full_ts[:,:,:,4],axis=(1,2))
    single_nu,single_psd  = psd(single_ts[:,1],dt=dt)
    single_nu *= 1e6 # Hz->muHz
    single_psd *= 1e-6 # ppm^2/Hz -> ppm^2/muHz 
    single_ts_SC = np.sum(full_ts_SC,axis=(1,2))/float(NGroup*NCamera)
    
    if(Verbose):
            print ('standard deviation of the averaged light-curves: %f ' % np.std(single_ts))

    if(MC):
        StarName = ("%7.7i%3.3i") % (StarID,iMC)
    else:
        StarName = ("%10.10i") % StarID
            
    fname = OutDir + StarName+ '.dat'
    if(Verbose):
        print ('saving the simulated light-curve as: %s' % fname)
    
    def ppar(par):
        n = len(par)
        i = 0 
        s = ''
        for u in list(par.items()):
            s += ' %s = %g' % u
            if (i < n-1):
                s += ', '
            i += 1
        return s
    
    hd = ''
    hd += ('StarID = %10.10i\n') % (StarID)  
    hd += ("Master_seed = %i\n") % (MasterSeed)
    hd += ("Version = %7.2f\n") % (__version__)
    
    
    if(FullOutput):
        full_ts = full_ts.reshape((nt*NGroup*NCamera,5))  
        np.savetxt(fname,full_ts,fmt='%12.2f %20.15e %1i %1i %1i',header=hd + '\nTime [s], Flux variation [ppm], Group ID, Camera ID, Flag')
    elif(MergedOutput):
        merged_ts = np.zeros((nt,NGroup,4))
        for G in range(NGroup):
            merged_ts[:,G,0] = rebin1d(full_ts[:,G,:,0].flatten(),nt)/float(NCamera)
            merged_ts[:,G,1] = rebin1d(full_ts[:,G,:,1].flatten(),nt)/float(NCamera)
            merged_ts[:,G,2] = G+1
            merged_ts[:,G,3] = rebin1d(full_ts[:,G,:,4].flatten(),nt)
        merged_ts = merged_ts.reshape((nt*NGroup,4)) 
        np.savetxt(fname,merged_ts,fmt='%12.2f %20.15e %1i %1i',header=hd + '\nTime [s], Flux variation [ppm], Group ID, Flag')
    else:
        np.savetxt(fname,single_ts,fmt='%12.2f %20.15e %1i',header=hd + '\nTime [s], Flux variation [ppm], Flag')
    
    hd += '# star parameters:\n'
    hd += (' teff = %f ,logg = %f\n') % (StarTeff, StarLogg)  
    hd += ppar(opar[0])
    hd += '\n# observations parameters:\n'
    hd += ppar(opar[1])
    hd += '\n# oscillation parameters:\n'
    hd += ppar(opar[2])
    hd += '\n# granulation parameters:\n'
    hd += ppar(opar[3])
    hd += '\n# activity parameters:\n'
    hd += ppar(opar[4])
    
    fname = OutDir + StarName+ '.txt'
    fd = open(fname,'w')
    fd.write(hd)
    fd.close()
    #fname = OutDir + StarName+ '.yaml'
    #shutil.copy2(config,fname)
    
    if(MC):
        MasterSeed = np.random.randint(0, 1073741824 + 1)
        np.random.seed(MasterSeed)
        seeds = np.random.randint(0, 1073741824 + 1,size=NGroup*NCamera+2)

    
if(Plot):   
    # releasing unused variables
    full_ts = None
    merged_ts = None
    if(not ExtendedPlots):
        full_ts_SC = None
    
    plt.figure(100)
    plt.clf()
    plt.title(StarName)
    

    plt.plot(single_nu[1:],single_psd[1:],'grey',label='simulated (raw)')
    win = opar[2]['numax']/100.
    m = int(round(win/single_nu[1]))
    p = int(nnu/m)
    num = rebin1d(single_nu[0:p*m],p)/float(m)
    if (DataSystematic is not None):
        _,psdsc = psd(single_ts_SC,dt=dt)
        psdsc *= 1e-6
        psdscm = rebin1d(psdsc[0:p*m],p)/float(m)
        plt.plot(single_nu[1:],psdsc[1:],'b:',label='systematics')

    psdm = rebin1d(single_psd[0:p*m],p)/float(m)
    if(W>0.):
        psdr = np.ones(mps_nf.size)*W**2*1e-6/NCamera/NGroup # random noise component
    else:
        psdr = 0.
    psdme = 0.5*mps_nf +  psdr # mean expected PSD for all camera
    
    plt.plot(num[1:],psdm[1:],'k',lw=2,label='simulated (mean)') # simulated spectrum, all camera
    if (DataSystematic is not None):
            plt.plot(num[1:],psdscm[1:],'m',label='systematics (mean)')

    # factor 1/2 to convert  the PSD from single-sided to double-sided PSD
    ## plt.plot(f[1:], psdme[1:] ,'b',lw=2,label='star+instrument')  # All Camera
    plt.plot(f[1:], 0.5*mps_nf[1:],'r',lw=2,label='star') # noise free
    if(W>0.):
        plt.plot(f[1:], psdr[1:],'g',lw=2,label='random noise') # all Camera
#    plt.plot(f[1:], 0.5*( (mps_SC[1:]  - 2*W**2*1e-6/NCamera) /(NGroup)),'m',lw=2,label='systematics') # all Camera
    
    fPT,psdPT = platotemplate(Duration, dt=1., V=11., n=NCamera*NGroup, residual_only=True)
    plt.plot(fPT[1:]*1e6, psdPT[1:]*1e-6,'k',ls='--',lw=2,label='systematics (requierements)')
    
    plt.loglog()
    plt.xlabel(r'$\nu$ [$\mu$Hz]')  
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')
    plt.axis(ymin=psdme[-1]/100.,xmax=np.max(single_nu[1:]))
    plt.legend(loc=0)
    if(Pdf):
        fname = OutDir + StarName+ '_fig1.pdf'
    else:
        fname = OutDir + StarName+ '_fig1.png'
    plt.savefig(fname)

    plt.figure(101)
    plt.clf()
    plt.title(StarName)
    plt.plot(time/86400.,single_ts[:,1]*1e-4,'grey')
        
    m = int( round(max(3600.,Sampling)/Sampling))
    p = int(time.size/m)
    tsm = rebin1d(single_ts[0:p*m,1],p)/float(m)
    timem = rebin1d(time[0:p*m],p)/float(m)
    
        
    plt.plot(timem/86400.,tsm*1e-4,'k')
    plt.xlabel('Time [days]')  
    plt.ylabel('Relative flux variation [%]')
    if(Pdf):
        fname = OutDir + StarName+ '_fig5.pdf'
    else: 
        fname = OutDir + StarName+ '_fig5.png'
    plt.savefig(fname)


    if(ExtendedPlots):

        plt.figure(102)
        plt.clf()
        plt.title(StarName)
        numax =  opar[2]['numax']
        Hmax = opar[2]['Hmax']  
        u =     (num> numax*0.5) & (num < numax*1.5)
        plt.plot(num[u],psdm[u],'k',lw=2) # simulated spectrum, all camera
    
        plt.loglog()
        plt.xlabel(r'$\nu$ [$\mu$Hz]')  
        plt.ylabel(r'[ppm$^2$/$\mu$Hz]')    
        if(Pdf):
            fname = OutDir + StarName+ '_fig2.pdf'
        else:
            fname = OutDir + StarName+ '_fig2.png'
        plt.savefig(fname)
    
    
        plt.figure(103)
        plt.clf()
        plt.title(StarName)
        u =     (f> numax*0.5) & (f < numax*1.5)
        plt.plot(f[u], 0.5*mps_nf[u],'r',lw=2,label='star') # noise free
        plt.xlabel(r'$\nu$ [$\mu$Hz]')  
        plt.ylabel(r'[ppm$^2$/$\mu$Hz]')    
        if(Pdf):
            fname = OutDir + StarName+ '_fig4.pdf'
        else: 
            fname = OutDir + StarName+ '_fig4.png'
        plt.savefig(fname)

        plt.figure(104)
        plt.clf()
        plt.title(StarName+': systematic LCs')
        for i in range(NGroup):
            for j in range(NCamera):
                plt.plot(time/86400.,full_ts_SC[:,i,j])
        plt.plot(time/86400.,single_ts_SC,'k',lw=2)
        plt.xlabel('Time [days]')  
    
    plt.draw()
    plt.show()


if(Verbose):
    print ('done')
    
if(Verbose | Plot):
    s=input('type ENTER to finish')



