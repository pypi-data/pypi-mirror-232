import bilby.gw.source
import numpy as np

#dchiMinus2 is dipole radiation in PPE frame, c.f. https://arxiv.org/pdf/2112.06861.pdf Eqs.(4-5). 
#See bilby.gw.source for the definition of arguments except dchiMinus2
#https://github.com/lscsoft/bilby/blob/master/bilby/gw/source.py

#define dipole wavefom by myself.
def dipole_radiation(frequency_array, mass_1, mass_2, luminosity_distance, a_1, tilt_1,
        phi_12, a_2, tilt_2, phi_jl, theta_jn, phase, lambda_1, lambda_2, dchiMinus2, 
        **kwargs):
    

    waveform = bilby.gw.source.lal_binary_neutron_star(
        frequency_array, mass_1, mass_2, luminosity_distance, a_1, tilt_1,
        phi_12, a_2, tilt_2, phi_jl, theta_jn, phase, lambda_1, lambda_2,
        **kwargs)
    hplus = waveform['plus']
    hcross = waveform['cross']
    
    GMsun_over_c3 = 4.925491025543575903411922162094833998e-6 # seconds
    eta = (mass_1 * mass_2) / ( mass_1 + mass_2 )**2
    freq_ISCO_2pn  = 1 / ( np.pi * (mass_1+mass_2) * GMsun_over_c3 ) * ( 3/ (14 * eta) * (1-np.sqrt( 1 - 14/9*eta ))) **  (3/2)
    # Cutoff at ISCO frequency.

    coefficient = np.zeros(len(hplus), dtype = 'complex128')
    index = np.where( (hplus!=0) & (frequency_array <= freq_ISCO_2pn) )
    coefficient[index] =  1j * 3.0/ (128.0 * eta) * (np.pi * GMsun_over_c3 * frequency_array[index] * (mass_1 + mass_2)) ** (-7/3)
    #the mass_1 and mass_2 are in the detector frame, so the redshift is absent here.
    #https://iopscience.iop.org/article/10.3847/1538-4357/ac1d4f Eq.(7). 
    #In this paper, the authors set c=1.

    hplus  *= np.exp(dchiMinus2 * coefficient)
    hcross *= np.exp(dchiMinus2 * coefficient)

    return dict(plus=hplus, cross=hcross)