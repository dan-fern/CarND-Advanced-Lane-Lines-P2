### Define a class to receive the characteristics of each line detection
import numpy as np

class Line( ):
    
    def __init__(self):
        
        # was the line detected in the last iteration?
        self.detected = False  
        
        # x values of the last n fits of the line
        self.recent_xfitted = [ ]
        
        #average x values of the fitted line over the last n iterations
        self.bestx = None     
        
        #polynomial coefficients averaged over the last n iterations
        self.best_fit = None  
        
        #polynomial coefficients for the most recent fit
        self.current_fit = [ np.array( [ False ] ) ]  
        #self.current_fit = None
        
        #radius of curvature of the line in some units
        self.radius_of_curvature = None 
        
        #distance in meters of vehicle center from the line
        self.line_base_pos = None 
        
        #difference in fit coefficients between last and new fits
        self.diff = np.array( [ 0, 0, 0 ], dtype='float' ) 
        
        #number of detected pixels
        self.px_count = None
    
    def add_fitted_line( self, fit, indices ):
        
        # add a new fit to the line, up to n
        if fit is not None:
            
            if self.best_fit is not None:
                
                # if a best fit, compare to previous
                self.diff = abs( fit - self.best_fit )
            
            if ( self.diff[0] > 0.001 or self.diff[1] > 1.0 or self.diff[2] > 100. ) \
                    and len( self.current_fit ) > 0:
                
                # break if bad fit unless no current fits
                self.detected = False
            
            else:
                
                self.detected = True
                self.px_count = np.count_nonzero( indices )

                # keep most recent fits
                if len( self.current_fit ) > 5:
                    self.current_fit = self.current_fit[len( self.current_fit )-5:]
                
                # clear out initial false entries
                if self.current_fit == [ ] or len( self.current_fit[0] ) != 1:
                    self.current_fit.append( fit )
                else:
                    self.current_fit[0] = fit

                self.best_fit = np.average( self.current_fit, axis=0 )
                       
        else:
            
        # or remove one from the history, if not found
            self.detected = False
            
            if len( self.current_fit ) > 0:
                
                # throw out oldest fit
                self.current_fit = self.current_fit[ :len( self.current_fit ) - 1 ]
            
            if len( self.current_fit ) > 0:
                
                # if there are still any fits in the queue, best_fit is their average
                self.best_fit = np.average( self.current_fit, axis=0 )

###