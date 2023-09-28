import compPy.comp as comp

from scipy.signal import medfilt
from scipy.ndimage import map_coordinates
from scipy.fftpack import fft, ifft

from compPy.printProgressBar import printProgressBar

# FUNCTION debugSetPlots, nx,ny,nt,max_track_length,velocityImage
#     ; set displays for space time diagram and prograde/retrograde wave components
#     window,0,xs=nx,ys=ny,retain=2,xpos=0,ypos=700
#     window,1,xs=nx,ys=ny,retain=2,xpos=nx+10,ypos=700
#     ;window,2,xs=nt*2,ys=npt*2,title='Space-Time Diagram'
#     window,3,xs=nt*2,ys=max_track_length*2,xpos=0,ypos=2*max_track_length+45,title='Prograde Filtered'
#     window,4,xs=nt*2,ys=max_track_length*2,xpos=0,ypos=4*max_track_length+90,title='Retrograde Filtered'
#     window,8,xs=900,ys=600

#     device,decomposed=0

#     wset,0    & img1=velocityImage
#     blue_red & tvlct, brr,brg,brb, /get
#     brr[255] = 0 & brg[255] = 0 & brb[255] = 0
#     tvlct, brr,brg,brb
#     img1 = bytscl(img1,-8,8,top=254)
#     tv, img1
#     wset,1
#     loadct, 13, /silent & tvlct, r,g,b, /get
#     r[255] = 255 & g[255] = 255 & b[255]= 255
#     tvlct, r,g,b
#     img2=bytscl(angle,-90,90,top=254)
#     tv,img2

#     return, {r:r,g:g,b:b,brr:brr,brg:brg,brb:brb}
# END

# FUNCTION debugPlot,img1,angle,temp_track,nx,ny,nt,debugPlotColors,pro_vel,ret_vel,currentTrackLength
#     ; display space time diagram and prograde/retrograde wave components

#     img1 = bytscl(img1,-8,8,top=254)
#     img2 = bytscl(angle,-90,90,top=254)

#     img1(temp_track.xCoordinates,temp_track.yCoordinates)=255 ;put track into displayed images
#     img2(temp_track.xCoordinates,temp_track.yCoordinates)=255

#     wset,0                      ;re-display velocity image with track
#     tvlct, debugPlotColors.brr,debugPlotColors.brg,debugPlotColors.brb
#     tv,img1
#     wset,1                      ;re-display angle image with track
#     tvlct, debugPlotColors.r,debugPlotColors.g,debugPlotColors.b
#     tv,img2
#     loadct, 70, /silent
#     wset,3 & tvscl,bytscl(rebin(pro_vel,nt*2,currentTrackLength*2,/sample),-2,2)
#     wset,4 & tvscl,bytscl(rebin(ret_vel,nt*2,currentTrackLength*2,/sample),-2,2)
#     loadct, 39, /silent
#     wset,8
#     !p.multi=[0,2,2]
#     return,0
# END

def findTrack(temp_track,hemisphere,nx,ny,i,factor,noPixelsTrack,angle,stepSize,low_mask_rad,upper_mask_rad)
    """Calculates which x and y direction to follow
    """

    returnValue=0
    #Use of hemisphere ensure signal always steps away from occulting disk
    sign=-1 if factor == 0 else sign=1
    anglePrevious=temp_track['angles',i+sign]
    potential_x = temp_track['xCoordinates',i+sign]-hemisphere*stepSize*cos( (anglePrevious+factor)*!dtor)
    temp_track['xCoordinates',i]=min( max(potential_x, 0.) , nx-1 )

    potential_y = temp_track['yCoordinates',i+sign]-hemisphere*stepSize*sin( (anglePrevious+factor)*!dtor)
    temp_track['yCoordinates',i]=min( max(potential_y, 0.) , nx-1 )

    nextX = min( max( np.floor(temp_track['xCoordinates',i]+0.5), 0) , nx-1)
    nextY = min( max( np.floor(temp_track['yCoordinates',i]+0.5), 0) , ny-1)
        
    pixcheck= ( (nextX-nx/2.+0.5)**2 + (nextY-ny/2.+0.5)**2 )**0.5
    if (pixcheck < low_mask_rad) or (pixcheck > upper_mask_rad): 
        temp_track['xCoordinates',i] = 0.
        temp_track['yCoordinates',i] = 0.
        returnValue = 1
    
    if returnValue == 0: 
        noPixelsTrack=noPixelsTrack+1
             
        temp_track['angles',i]=angle[nextX,nextY]  

        # if big difference in adjacent angles, resolve 180 degree ambiguity
        # by choosing angle closest to ang_track(i-1)
        angleDifference=temp_track['angles',i]-temp_track['angles',i+sign]                 
        if abs(angleDifference) > 90.:
            temp_track['angles',i]-=180. if angleDifference > 0. else temp_track['angles',i]+=180.

    return returnValue 

def calc_frequency(N,T):
    """
    Calculates frequency values for DFT

    Parameters
    -----------
    N - int
        number of elements in a particular dimension
    T - floating-point 
        number giving the sampling interval
    """
    X = np.arange( 0, (N - 1)//2 ) + 1 
    is_N_even = (N % 2) == 0
    if (is_N_even) :
        freq = np.concatenate( ( np.append(X, N//2) , -N//2 + X) ) 
    else:
        freq = np.concatenate( (X, -(N//2 + 1) + X) ) 

    freq=np.append(0, freq) /(N*T) 

    return freq


def filter_velocity(velocityTrack,currentTrackLength,nt,freq_filter)
    """ Filter inward and outward waves
    """

    filt_2d=np.tile( freq_filter, (currentTrackLength,1) )

    velocityTrack=velocityTrack - velocityTrack.mean()
    velocityTrack=velocityTrack - np.transpose( np.tile( velocityTrack.mean(axis=1), (nt,1) ), (1,0) ) # remove temporal mean
    
    velocityFFT = fft(velocityTrack)*filt_2d
   
    # Doesn't need correct sampling time
    freq = np.tile( calc_frequency(nt, 1), (currentTrackLength,1))
    wave_num = np.tile( calc_frequency(currentTrackLength, 1), (nt,1)).T
    phase_sign = np.sign( freq * wave_num )

    pro_trans = velocityFFT.copy() # select prograde waves (assume nt even, currentTrackLength odd)
    pro_trans [(phase_sign > 0 )] = 0
    progradeVelocity = ifft( pro_trans ).real

    ret_trans = velocityFFT.copy()            # select retrograde waves
    pro_trans [(phase_sign < 0 )] = 0
    retrogradeVelocity = ifft( ret_trans ).real

    return {'retrograde':retrogradeVelocity,'prograde':progradeVelocity}




def calc_phase_speed(speeds)

     relativeSpeedPrograde=speeds.prograde/speeds.progradeError
     relativeSpeedRetrograde=abs(speeds.retrograde)/speeds.retrogradeError
     relativeError=1.0/speeds.progradeError^2 + 1.0/speeds.retrogradeError^2

     speeds.phaseSpeed=(relativeSpeedPrograde^2 + relativeSpeedRetrograde^2)/relativeError
     speeds.phaseSpeedError=relativeError

     return 



def space_time_run(date, velocity, angle, index,config, name_addon, 
                       debug=False, wr_speeds=False):
    """
                     
        PURPOSE:  Procedure to compute space-time diagram of velocity time series over a whole image.
        
        
        OUTLINE:  The track is computed from the angle map. Velocities are then interpolated onto a time-distance
                  map. The mean value of the velocity for the map is subtracted. The temporal mean for each position
                  along the track is also subtracted before FFT. FFT of map taken and high spatial and temporal
                  frequencies are removed. Then separates prograde and retrograde components (i.e., where w=ck & w=-ck).
                  Inverse fourier transform is taken for velocities which are then sent to compute_speed to compute the
                  phase speed. 
        
        
        INPUTS: data- date of observations
                velocity - Aligned + trimmed Doppler velocity cube
                angle - array of angles calculated form coherence islands (see wave_tracking.pro + McIntosh et al. 2008)
                config - general useful variables
                name_addon - additional quantifier to be added to the name of the .sav filter 
        
        OPTIONAL INPUTS: /debug - Use to debug code + process - opens multiple windows + prints to screen
                         /wr_speed - Saves pro/retro - grade velocity maps
                         max_track_length - length of track to use for cross-correlation, maximum useful length appears to 
                                    be around 21. Signal only correlates well over sort distances. Specify in comp_config.pro file
                        
        
        CALLS: compute_speed.pro 
        
        
        HISTORY: Created S Tomczyk
                - Fixed minor bug for dealing with tracks that are shorter than specified track length.
                  Turned continue's to break's - if track hits boundary it stops R Morton 11/2014 
                - Added if statements to debug only sections of code - hopefully reduce run time.
                  Edited out power calculation to reduce run time  
                  Attempted to remove bad series from calculation by looking at RMS values
                  - tiny values of RMS suggest incomplete series.
                  Changed start pixel selection criteria based on angle value to mask value 
                  Added break statement if track hits bad mask value
                  Applied Median smoothing of wave angle map to reduce noise  R Morton 03/2016
                - v0.3 (RJM 05/2019) Introducing versioning to keep track of code development. Given past major changes, 
                  the first numbered version is as version 0.3.
        
        TO DO: Is there a smarter way to interpolate velocity onto track - at the moment there is a for loop over time.
               * Fourier filtering causes artefacts - 'curled up/down' ends due to edge effects - increases gradient!
                                                    -  max propagation speed of ~1347 km/s (highest frequency * track length). 
    """

    cubes = comp.cp_load(date,['cube_v'])
    cube_v = cubes['cube_v'].copy()
    index = cubes['index'].copy()
    mask = cubes['mask'].copy()

    #Define constants & variables from index
    ntime,ny,nx=cube_v.shape


    norm_cadence=index['header']['NORM_CADENCE']
    spatialSampling=index['header']['XSCALE']

    low_mask_rad= config.lowerMaskRadius
    upper_mask_rad = config.upperMaskRadius

    max_track_length=config.maxTrackLength #number of steps to map along track (make odd)
    stepSize=1.0      #step size along track

    number_lag_values=config.numberLagValues

    #number of time points to use (make even)
    nt = ntime if  (ntime % 2) == 0 else nt = ntime-1
    velocity=cube_v[0:nt-1, :, :].copy()

    #===========================
    #Empty track template
    track={"length": max_track_length,
           "angles": np.zeros(max_track_length),
           "xCoordinates": np.zeros(max_track_length),
           "yCoordinates": np.zeros(max_track_length) 
           }

    midPoint=int(max_track_length/2)

    # x = FINDGEN((nt - 1)/2) + 1
    # is_nt_even = (nt MOD 2) EQ 0
    # if (is_nt_even) then $
    #   freq = [0.0, X, nt/2, -nt/2 + X]/(nt*norm_cadence) $
    # else $
    #   freq = [0.0, X, -(nt/2 + 1) + X]/(nt*norm_cadence)

    # track.freq=rebin(freq,nt,npt)                         

    # x = FINDGEN((max_track_length - 1)/2) + 1
    # is_max_track_length_even = (max_track_length MOD 2) EQ 0
    # if (is_max_track_length_even) then $
    #   freq = [0.0, X, max_track_length/2, -max_track_length/2 + X]/(max_track_length*spatialSampling) $
    # else $
    #   freq = [0.0, X, -(max_track_length/2 + 1) + X]/(max_track_length*spatialSampling)

    # #sp_freq
    # track.spatialFreq=rebin(transpose(sf),nt,npt)

    #Set up filter
    nspec=nt//2
    freq   = np.arange(0,nspec) / ( nspec * 2 * index.NORM_CADENCE)
    freq_filter = np.exp( 
                         -( freq -  config.freq_filter.centralFrequency )**2 / config.freq_filter.width**2 
                         )
    freq_filter[0] = 0.               # set dc to zero
    freq_filter[ freq < .001 ] = 0.   # set low frequencies to zero
    freq_filter = freq_filter/freq_filter.sum()
    freq_filter = [freq_filter, freq_filter[::-1] ]
    freq_filter[ freq_filter <= 1e-10 ] = 0 # stops underflow errors

    angle=medfilt(angle, kernel_size=3) #Median smoothing of wave angle map to reduce noise


    # Define x and y limits for map
    locationLimits = (mask == 1).nonzero()
    xstart = (locationLimits[1] % nx ).min()  
    xend = (locationLimits[1] % nx ).max()
    ystart = (locationLimits[0] // ny ).min()
    yend = (locationLimits[0] // ny ).max()
    pixels2process = len(locationLimits[0] )

    #Already done in wave_tracking_v2
    x= np.arange(0,nx)- nx/2.+0.5
    rad=( x**2 + x[:,np.newaxis]**2 )**0.5

    #Define dictionary of arrays to store prograde and retrograde quantities 
    speeds={'prograde': np.zeros( (ny, nx) ),
            'retrograde': np.zeros( (ny, nx) ),
            'phaseSpeed': np.zeros( (ny, nx) ),
            'progradeError': np.zeros( (ny, nx) ),
            'retrogradeError': np.zeros( (ny, nx) ),
            'phaseSpeedError': np.zeros( (ny, nx) ),
            'sign': np.zeros( (ny, nx) )
            }


    if wr_speeds == True: 
         prograde_cube=np.zeros( (nt, ny, nx) )
         retrograde_cube=np.zeros( (nt, ny, nx) )



    ###############################################################
    #Main section of the routine
    ###############################################################

    print('Starting processing...')
    count=0

    IF debug == TRUE: debugPlotColors=debugSetPlots(nx,ny,nt,max_track_length,velocity[*,*,0])

    for yPosition in np.arange(ystart,yend):
        for xPosition in np.arange(xstart,xend):

          
            if mask[yPosition, xPosition] == 1:
                
                 printProgressBar(count, pixels2process, prefix = 'Calculating speeds:', suffix = 'Complete', length = 30) 
             
                 temp_track=track.copy() #reinitialise temporary dictionary

                 temp_track['xCoordinates'][midPoint] = xPosition 
                 temp_track['yCoordinates'][midPoint] = yPosition
                 temp_track['angles'][midPoint] = angle[yPosition, xPosition]

                 noPixelsTrack=0
          
                 #  first, move out from cursor position 
                 hemisphere = 1 if xPosition <= nx//2-1 else hemisphere = -1
                 factor=0

                 for i in np.arange(midPoint+1, temp_track.length): 
                    res = findTrack(temp_track, hemisphere, nx, ny, i, factor,
                                    noPixelsTrack, angle, stepSize,
                                    low_mask_rad, upper_mask_rad
                                    )
                    if res == 1: break


                 #  next, move in from cursor position
                 factor=180
                 for i in np.arange(midPoint-1,-1,-1): 
                    res=findTrack(temp_track, hemisphere, nx, ny, i, factor,
                                  noPixelsTrack, angle, stepSize,
                                  low_mask_rad, upper_mask_rad
                                  )
                    if res == 1: break
                 

                 if noPixelsTrack < 4: continue #take at least 5 points in the track
                 
                 if noPixelsTrack < max_track_length: #Trim track arrays if necessary 
                    vals = (temp_track.xCoordinates != 0).nonzero()
                    xTrack = temp_track['xCoordinates', vals]
                    yTrack = temp_track['yCoordinates', vals]
                    currentTrackLength = len(vals)
                 else: 
                    currentTrackLength = max_track_length
                    xTrack = temp_track['xCoordinates']
                    yTrack = temp_track['yCoordinates']
                                     

                 velocityTrack = np.array( (nt, currentTrackLength) )

                 for i in np.arange(0, nt):
                    velocityTrack[i,:]=map_coordinates( velocity[i,:,:], np.vstack( (yTrack,xTrack) ) ) ###Needs checking

                 velocity_filt=filterVelocity(velocityTrack,currentTrackLength,nt,freq_filter)

                 if debug == True: 
                    resDebug=debugPlot(velocity[0,:,:], angle, temp_track, nx, ny, nt,
                                       debugPlotColors, pro_vel, ret_vel, currentTrackLength)

                 ##############################################################
                 # compute phase speeds of prograde, retrograde and combination
                      
                  
                  r=compute_speed(velocity_filt.prograde, spatialSampling, norm_cadence)#,number_lag_values)
                  speeds.prograde(xPosition,yPosition)=r[0]
                  speeds.progradeError(xPosition,yPosition)=r[1]
                
                  r=compute_speed(velocity_filt.retrograde ,spatialSampling, norm_cadence,/ret)#, number_lag_values,/ret)
                  speeds.retrograde[xPosition,yPosition]=r[0]
                  speeds.retrogradeError[xPosition,yPosition]=r[1]


                 # determine whether track is outward or inward, which determines sign of prograde and retrograde
                  speeds.sign[xPosition, yPosition]=- ( rad[ xTrack[0], yTrack[0]] - rad[ xTrack[currentTrackLength-1], yTrack[currentTrackLength-1]])/ 
                                  abs(rad[xTrack[0],yTrack[0]]-rad[xTrack[currentTrackLength-1],yTrack[currentTrackLength-1]])
                 
                 if wr_speeds == 1:
                    val=(xTrack == xPosition and yTrack == yPosition).nonzero()

                    #correction for track orientation
                    if speed.sign[xPosition,yPosition] > 0: 
                        prograde_cube[xPosition,yPosition,] = velocity_filt.prograde[:,currentTrackLength/2]
                        retrograde_cube[xPosition,yPosition,] = velocity_filt.retrograde[:,currentTrackLength/2]
                    else:
                        prograde_cube[xPosition,yPosition,] = velocity_filt.retrograde[:,currentTrackLength/2]
                        retrograde_cube[xPosition,yPosition,] = velocity_filt.prograde[:,currentTrackLength/2]
                
                 
                 if debug == True: !p.multi=0
                 count=count+1  
                 

result=calcPhaseSpeed(speeds)

##############################################################
# Save outputs
##############################################################

#nwlst = strcompress(string(config['numberWaveLengths']),/rem)
#save, file=config['outpath']+'speeds_'+name_addon+date+'_'+nwlst+'_'+config['freqst']+'.sav',speeds
     

#if wr_speeds eq 1 then begin
# save,file=config['outpath']+'pro_filtered_cube_'+name_addon+date+'.sav',prograde_cube
# save,file=config['outpath']+'ret_filtered_cube_'+name_addon+date+'.sav',retrograde_cube
#endif



