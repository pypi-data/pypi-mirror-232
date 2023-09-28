# -*- coding: utf-8 -*-
"""Yield strength model for aluminium.

The YieldStrength class has models for the following terms:
  - intrisic (i)
  - precipitates (ppt)
  - solid solution (ss)
  - dislocations (disl)
  - grains and subgrains (grain)

References
----------
 [1] O.R. Myhr, Ø. Grong and S.J. Andersen. "Modelling of the age hardening
     behaviour of Al-Mg-Si alloys".  Acta mater. 49 (2001) 65-75.
 [2] O.R. Myhr, Ø. Grong and C. Schäfer. "An Extended Age-Hardening Model
     for Al-Mg-Si Alloys Incorporating the Room-Temperature Storage and
     Cold Deformation Process Stages".  Metall. Mater. Trans. A46 (2015)
     2015-6019.
 [3] B. Holmedal. "Strength contributions from precipitates". Phil. Mag. Lett.
     95 (2015) 594-601.
 [4] M.F. Ashby.  Acta Metall. 14 (1979) 679.
"""
from __future__ import division
from __future__ import print_function

import os
import sys

import numpy as np
from numpy import pi, sqrt, log

try:
    import calm
except ImportError:
    dirname = os.path.dirname(__file__)
    sys.path.append(os.path.join(dirname, '..', '..', 'calm'))
    import calm

from calm.material_parameters import MaterialParameters
from calm.chemistry import ChemistrySizeDistribution
from calm.microstructure import Microstructure


class YieldStrengthError(Exception):
    """Base class for exceptions in this module."""
    pass


class YieldStrength(object):
    """Class implementing yield strength model based on microstructure data.

    Parameters
    ----------
    chem : instance of ChemistrySizeDistribution
        Description of the particle size distribution.
    microstructure : <Microstructure instance>
        Includes grain size, subgrain size and dislocation density, ...
    material : instance of MaterialParameters
        The default corresponds to aluminium.
    models : dict
        A dict mapping term names to the name of the model to use for this
        term.  If given it will replace the `models` attribute.  Otherwise
        the `models` attribute will point to a default model for each term.
    texture_model : "Taylor"
        Texture model.  Currently only the "Taylor" model is implemented.

    Attributes
    ----------
    terms : list
        List with considered terms.
    models : dict
        A dict mapping the name of considered terms to the name of the
        model to use for that term.  An easy way to replace individual
        models is to modify this attribute.
    chem : instance of ChemistrySizeDistribution
        Description of the particle size distribution.
    microstructure : <Microstructure instance>
        Includes grain size, subgrain size and dislocation density, ...
    """

    # A dict mapping the terms to a list of names of the different models
    # implementing this term
    _model_lists = {}
    _alias = {'intrinsic': 'i',
              'solid_solution': 'ss',
              'precipitate': 'ppt',
              'cluster': 'cl',
              'dislocation': 'disl',
              'grain': 'grain'}

    def __init__(self, chem, microstructure, material=None, models=None,
                 texture_model='Taylor', **kwargs):
        if isinstance(chem, ChemistrySizeDistribution):
            self.chem = chem
        else:
            raise TypeError('Expected type for "chem": ChemistrySizeDistribution')

        if isinstance(microstructure, Microstructure):
            self.microstructure = microstructure
        elif isinstance(microstructure, dict):
            self.microstructure = Microstructure(**microstructure)
        else:
            raise TypeError('Expected type for "microstructure": Microstructure')

        if isinstance(material, MaterialParameters):
            self.material = material
        elif isinstance(material, dict):
            self.material = MaterialParameters(**material)
        elif material is None:
            self.material = MaterialParameters(elements=chem.elements)
        else:
            raise TypeError('Expected type for "material": MaterialParameters')

        self.models = {}
        for term, items in self._model_lists.items():
            if items:
                self.models[term] = items[0]
        if isinstance(models, dict):
            for term, model in models.items():
                if term in self._alias:
                    term = self._alias[term]
                if term in self._model_lists:
                    if model:
                        if model in self._model_lists[term]:
                            self.models[term] = model
                        else:
                            self.models.pop(term, None)
                    else:
                        self.models.pop(term, None)

        self.texture_model = texture_model
        
        self.kwargs = kwargs

    terms = property(lambda self: list(self.models),
                     doc='List with names of considered terms.')

    @classmethod
    def list_terms(cls):
        """Returns a list of implemented terms."""
        return list(cls._model_lists)

    @classmethod
    def list_models(cls, term):
        """Returns a list with the name of models implemented for `term`."""
        if term in cls._model_lists:
            return cls._model_lists[term][:]
        else:
            raise YieldStrengthError('No such term:', term)

    def get_method(self, term, model=None):
        """Returns reference to the method defining the model for `term`.
        If `model` is None, the default model is returned."""
        if term not in self._model_lists:
            raise YieldStrengthError(
                'Valid terms are: "%s". Got "%s"' %
                ('", "'.join(self._model_lists.keys()), term))
        if model is None:
            model = self._model_lists[term][0]
        elif model not in self._model_lists[term]:
            raise YieldStrengthError(
                'Valid models for "%s" are: "%s". Got "%s"' %
                (term, '", "'.join(self._model_lists[term]), model))
        return getattr(self, 'tau_%s_%s' % (term, model))

    def tau(self, models=None):
        """Returns the total shear stress in MPa.  The `models` argument has
        the same meaning as for the yieldstrength() method."""
        if models is None:
            models = self.models
        tau = 0.0
        for term, model in models.items():
            f = self.get_method(term, model)
            tau += f()
        return tau

    def yieldstrength(self, models=None, texture_model=None):
        """Returns the total Yield strength in MPa.

        Parameters
        ----------
        models : None | dict
            If given, use this dict instead of the `models` attribute.
        texture_model : None | string
            If given, use this texture model instead of the one specified with
            the `texture_model` attribute.
        """
        if  texture_model is None:
            texture_model = self.texture_model

        if texture_model == 'Taylor':
            MTaylor = self.microstructure.MTaylor
            tau = self.tau(models)
            sigma = MTaylor * tau
        else:
            raise YieldStrengthError('No such texture model: %s' %
                                     texture_model)
        return sigma

    def __str__(self):
        s = ['term     tau(MPa)  sigma(MPa)  model']
        for term in self.terms:
            tau = self.tau(models={term: self.models[term]})
            sigma = self.yieldstrength(models={term: self.models[term]},)
            model = self.models[term]
            s.append('%-8s %8.1f    %8.1f  %s' % (term, tau, sigma, model))
        s.append('--------------------------------------')
        s.append('total    %8.1f    %8.1f' % (self.tau(), self.yieldstrength()))
        return '\n'.join(s)


    # General model-dependent constants
    data_Myhr2015_Mr = 3.1          # Reference Taylor factor
    data_Myhr2015_b = 2.84e-10      # Burger's vector, m
    data_Myhr2015_Gshear = 27.0e+3  # Shear modulus, MPa

    #-------------------------------------------------------------------------
    #  Intrinsic (i)
    #-------------------------------------------------------------------------
    _model_lists['i'] = ['Myhr2015']

    def tau_i_Myhr2015(self):
        """Returns the intrinsic contribution to the shear stress
        in MPa using the model in Myhr2015."""
        Mr = self.data_Myhr2015_Mr
        return 10.0 / Mr


    #-------------------------------------------------------------------------
    #  Solid solution (ss)
    #-------------------------------------------------------------------------
    _model_lists['ss'] = ['Myhr2015']

    data_ss_Myhr2015_kss = {'Cu': 46.4 , 'Mg': 15.0 , 'Mn': 80.0 , 'Si': 33.0}

    def tau_ss_Myhr2015(self):
        """Returns the solid solution contribution to the shear stress
        in MPa using the model in Myhr2015."""
        kss = self.data_ss_Myhr2015_kss
        Css = self.chem.Css
        Mr = self.data_Myhr2015_Mr
        return sum(kss.get(e, 0) * Css[i] ** (2 / 3)
                   for i, e in enumerate(self.chem.elements)) / Mr


    #-------------------------------------------------------------------------
    #  Precipitates (ppt)
    #-------------------------------------------------------------------------
    _model_lists['ppt'] = ['Myhr2015', 'Myhr_Holmedal', 'Holmedal2015_needle',
                           'Ashby1979']

    data_ppt_Myhr2015_rshear_cluster = 7e-9  # critical radius for shear, m
    data_ppt_Myhr2015_rshear_hardening = 5e-9  # critical radius for shear, m
    data_ppt_Myhr2015_beta1 = 0.44
    data_ppt_Myhr2015_cluster = ['cluster']
    data_ppt_Myhr2015_hardening = None

    def tau_ppt_Myhr2015(self, cluster=None, hardening=None):
        """Returns the precipitate contribution to the shear stress
        in MPa using the model in Myhr2015.

        Parameters
        ----------
        cluster : sequence of str
            Name of all phases that should be considered as clusters.
            Default from the `data_ppt_Myhr2015_cluster` attribute, which
            defaults to "cluster".
        hardening : sequence of str
            Name of all phases that should be considered as hardening phases.
            Default from the `data_ppt_Myhr2015_hardening` attribute, which
            defaults to all phases not listed in `cluster`.
        """
        if cluster is None:
            cluster = self.data_ppt_Myhr2015_cluster
        if hardening is None:
            hardening = self.data_ppt_Myhr2015_hardening
        if hardening is None:
            hardening = set(self.chem.phasenames).difference(cluster)
        rshear_cl = self.data_ppt_Myhr2015_rshear_cluster
        rshear_hd = self.data_ppt_Myhr2015_rshear_hardening
        tau_cl = self.tau_ppt_Myhr2015_phases(cluster, rshear_cl)
        tau_hd = self.tau_ppt_Myhr2015_phases(hardening, rshear_hd)
        return np.sqrt(tau_cl**2 + tau_hd**2)

    def tau_ppt_Myhr_Holmedal(self, cluster=None, hardening=None):
        """Returns the precipitate contribution to the shear stress
        in MPa using the cluster contribution from Myhr2015 and the
        contribution from hardening ppt from Holmedal2015.

        Parameters
        ----------
        cluster : sequence of str
            Name of all phases that should be considered as clusters.
            Default from the `data_ppt_Myhr2015_cluster` attribute, which
            defaults to "cluster".
        hardening : sequence of str
            Name of all phases that should be considered as hardening phases.
            Default from the `data_ppt_Holmedal2015_needle` attribute, which
            defaults to all phases not listed in `cluster`.
        """
        if cluster is None:
            cluster = self.data_ppt_Myhr2015_cluster
        if hardening is None:
            hardening = self.data_ppt_Holmedal2015_needle
        if hardening is None:
            hardening = set(self.chem.phasenames).difference(cluster)
        rshear_cl = self.data_ppt_Myhr2015_rshear_cluster
        tau_cl = self.tau_ppt_Myhr2015_phases(cluster, rshear_cl)
        tau_hd = self.tau_ppt_Holmedal2015_needle(hardening)
        return np.sqrt(tau_cl**2 + tau_hd**2)

    def tau_ppt_Myhr2015_phases(self, phases, rshear):
        """Helper method that returns the shear stress contribution from
        all particles included in `phases`. `rshear` is the critical radius
        for shearing.

        Note
        ----
        It is not easy to read from Ref. [2], but from Ref. [1] it is
        clear that the obstacle strength of a particle with size `r` is

            F = 2 * beta * G * b**2 * min(1, r / rshear)
        """
        b = self.data_Myhr2015_b
        G = self.data_Myhr2015_Gshear
        beta1 = self.data_ppt_Myhr2015_beta1

        rmean = 0.0
        Fmean = 0.0
        l = 1.0
        mask = np.zeros(shape=(self.chem.ndomains, ), dtype=bool)
        for phase in phases:
            mask += self.chem.phasenames == phase
        if not np.any(mask):
            return 0.0
        F = 2 * beta1 * G * b**2 * np.clip(self.chem.rd / rshear, 0, 1)
        Nv = np.sum(self.chem.Nd[mask])
        if Nv >= 1.0:
            rmean = np.sum((self.chem.rd * self.chem.Nd)[mask]) / Nv
            Fmean = np.sum((F * self.chem.Nd)[mask]) / Nv
            l = np.sqrt((beta1 * G * b**2) / (Nv * rmean * Fmean))
        return Fmean / (b * l)

    data_ppt_Holmedal2015_needle = None  # Name of needle-shaped precipitates
    data_ppt_Holmedal2015_kappa = 1  # Empirical exponent
    data_ppt_Holmedal2015_mu = 19.8e3  # Shear modulus, MPa
    data_ppt_Holmedal2015_b = 2.86e-10  # Burgers vector, m
    data_ppt_Holmedal2015_ac = 5.6e-18  # Critical cross-section area, m²

    def tau_ppt_Holmedal2015_needle(self, needle=None):
        """Returns the contribution from needle-shaped precipitates to the
        shear stress in MPa using the model in Holmedal2015.

        Parameters
        ----------
        needle : sequence of str
            Name of all needle-shaped precipitates that should be
            included in this model.  Default from the
            `data_ppt_Holmedal2015_needle` attribute, which defaults
            to all phases.
        """
        chem = self.chem
        kappa = self.data_ppt_Holmedal2015_kappa
        mu = self.data_ppt_Holmedal2015_mu
        b = self.data_ppt_Holmedal2015_b
        #l0 = self.data_ppt_Holmedal2015_l0
        ac = self.data_ppt_Holmedal2015_ac

        if isinstance(needle, str):
            needle = [needle]
        elif needle is None:
            needle = self.data_ppt_Holmedal2015_needle
        if needle is None:
            needle = set(chem.phasenames)
        mask = np.zeros((chem.ndomains, ), dtype=bool)
        for phase in needle:
            mask += chem.phasenames == phase
        Nd = chem.Nd[mask]
        r = chem.rd[mask]

        if np.allclose(chem.shape, 1):
            # aspect seems not to be given, derive it from: Omega = sqrt(5 * l)
            k = 0.190 * 1e-9
            V = 4 * pi / 3 * r ** 3
            l = sqrt( V / k )                  # precipitate lengths - Du et al 2016
            Omega = sqrt(5 * l)                # l / sqrt(cross section area)
        else:
            l = 2 * chem.shape ** (2/3) * r
            Omega = sqrt(3 / pi) * chem.shape

        Nv = np.sum(Nd)
        lmean = np.sum(l * Nd) / Nv
        a = (l / Omega) ** 2
        i1 = a < ac
        i2 = a >= ac
        fmean = 1 / (Nv * lmean) * (
            1 / ac**kappa * np.sum(
                (l ** (2 * kappa + 1) / Omega ** (2 * kappa) * Nd)[i1]) +
            np.sum((l * Nd)[i2]))
        # There is a misprint in Eq. 14 in Holmedal2015 which is corrected below
        return 0.3 * mu * b * sqrt(3 * sqrt(3) * lmean * Nv * fmean**3) * (
            1 - fmean**5 / 6)

    #-------------------------------------------------------------------------

    def tau_ppt_Ashby1979(self):
        """Returns the contribution from non-deformable particles
        (dispersoids) due to the Orowan bypass stress by Ashby 1979 [4].

        The current implementation assumed all particles to be non-deformable.
        """
        chem = self.chem
        A = 0.5
        b = self.data_Myhr2015_b
        G = self.data_Myhr2015_Gshear

        tau = 0.0
        for j in range(1, chem.nphases):
            f = chem.volfrac[j]
            r = chem.rmean[j]
            lambda_ = 0.8 * (sqrt(pi / f) - 2) * r
            tau += A * G * b / (1.24 * 2 * pi) * log(lambda_ / b) / lambda_

        return tau
    

    #-------------------------------------------------------------------------
    #  Dislocations (disl)
    #-------------------------------------------------------------------------
    _model_lists['disl'] = ['Myhr2015']

    data_disl_Myhr2016_alpha = 0.3

    def tau_disl_Myhr2015(self):
        """Returns the dislocation contribution to the shear stress
        in MPa using the model in Myhr2015."""
        b = self.data_Myhr2015_b
        G = self.data_Myhr2015_Gshear
        alpha = self.data_disl_Myhr2016_alpha
        return alpha * G * b * np.sqrt(self.microstructure.rho_i)


    #-------------------------------------------------------------------------
    #  Grains and subgrains (grain)
    #-------------------------------------------------------------------------
    _model_lists['grain'] = ['Alflow', 'HallPetch']

    data_grain_Alflow_alpha2 = 2.0

    def tau_grain_Alflow(self):
        """Returns contribution (in MPa) to the shear stress from grains and
        subgrains.  Constants are taken from the Alflow model."""
        b = self.data_Myhr2015_b
        G = self.data_Myhr2015_Gshear
        alpha2 = self.data_grain_Alflow_alpha2
        m = self.microstructure
        return alpha2 * G * b * (1 / m.grainsize + 1 / m.delta)

    data_grain_HallPetch_k = 0.0791  # MPa m^(-1/2)

    def tau_grain_HallPetch(self):
        """Returns contribution (in MPa) to the shear stress from grains and
        subgrains.  Constants are taken from the Alflow model."""
        k = self.data_grain_HallPetch_k
        m = self.microstructure
        return k * sqrt(1 / m.grainsize + 1 / m.delta)


##############################################################################
#
#  Subclass for AMPERE
#
##############################################################################

class YieldStrength_AMPERE(YieldStrength):

    def get_constant(self, name, values):
        """"Returns the value of a model constant given its name. If no
        value is given by the user (through kwargs), the default value is
        the hardcoded one."""
        default = getattr(self, 'data_' + name, None)
        return values.get(name, default)
                
    #-------------------------------------------------------------------------
    #  Precipitates (ppt)
    #-------------------------------------------------------------------------
    def tau_ppt_Myhr2015(self, cluster=None, hardening=None):
        """Returns the precipitate contribution to the shear stress
        in MPa using the model in Myhr2015 with free constants.

        Parameters
        ----------
        cluster : sequence of str
            Name of all phases that should be considered as clusters.
            Default from the `data_ppt_Myhr2015_cluster` attribute, which
            defaults to "cluster".
        hardening : sequence of str
            Name of all phases that should be considered as hardening phases.
            Default from the `data_ppt_Myhr2015_hardening` attribute, which
            defaults to all phases not listed in `cluster`.
        """
        if cluster is None:
            cluster = self.get_constant('ppt_Myhr2015_cluster', self.kwargs)
        if hardening is None:
            hardening = self.get_constant('ppt_Myhr2015_hardening', self.kwargs)
        if hardening is None:
            hardening = set(self.chem.phasenames).difference(cluster)
        rshear_cl = self.get_constant('ppt_Myhr2015_rshear_cluster', self.kwargs)
        rshear_hd = self.get_constant('ppt_Myhr2015_rshear_hardening', self.kwargs)
        tau_cl = self.tau_ppt_Myhr2015_phases(cluster, rshear_cl)
        tau_hd = self.tau_ppt_Myhr2015_phases(hardening, rshear_hd)
        return np.sqrt(tau_cl**2 + tau_hd**2)

    def tau_ppt_Myhr_Holmedal(self, cluster=None, hardening=None):
        """Returns the precipitate contribution to the shear stress
        in MPa using the cluster contribution from Myhr2015 and the
        contribution from hardening ppt from Holmedal2015.

        Parameters
        ----------
        cluster : sequence of str
            Name of all phases that should be considered as clusters.
            Default from the `data_ppt_Myhr2015_cluster` attribute, which
            defaults to "cluster".
        hardening : sequence of str
            Name of all phases that should be considered as hardening phases.
            Default from the `data_ppt_Holmedal2015_needle` attribute, which
            defaults to all phases not listed in `cluster`.
        """
        if cluster is None:
            cluster = self.get_constant('ppt_Myhr2015_cluster', self.kwargs)
        if hardening is None:
            hardening = self.get_constant('ppt_Holmedal2015_needle', self.kwargs)
        if hardening is None:
            hardening = set(self.chem.phasenames).difference(cluster)
        rshear_cl = self.get_constant('ppt_Myhr2015_rshear_cluster', self.kwargs)
        tau_cl = self.tau_ppt_Myhr2015_phases(cluster, rshear_cl)
        tau_hd = self.tau_ppt_Holmedal2015_needle(hardening)
        return np.sqrt(tau_cl**2 + tau_hd**2)

    def tau_ppt_Myhr2015_phases(self, phases, rshear):
        """Helper method that returns the shear stress contribution from
        all particles included in `phases`. `rshear` is the critical radius
        for shearing.

        Note
        ----
        It is not easy to read from Ref. [2], but from Ref. [1] it is
        clear that the obstacle strength of a particle with size `r` is

            F = 2 * beta * G * b**2 * min(1, r / rshear)
        """
        b = self.get_constant('Myhr2015_b', self.kwargs)
        G = self.get_constant('Myhr2015_Gshear', self.kwargs)
        beta1 = self.get_constant('ppt_Myhr2015_beta1' ,self.kwargs)

        rmean = 0.0
        Fmean = 0.0
        l = 1.0
        mask = np.zeros(shape=(self.chem.ndomains, ), dtype=bool)
        for phase in phases:
            mask += self.chem.phasenames == phase
        if not np.any(mask):
            return 0.0
        F = 2 * beta1 * G * b**2 * np.clip(self.chem.rd / rshear, 0, 1)
        Nv = np.sum(self.chem.Nd[mask])
        if Nv >= 1.0:
            rmean = np.sum((self.chem.rd * self.chem.Nd)[mask]) / Nv
            Fmean = np.sum((F * self.chem.Nd)[mask]) / Nv
            l = np.sqrt((beta1 * G * b**2) / (Nv * rmean * Fmean))
        return Fmean / (b * l)

    def tau_ppt_Holmedal2015_needle(self, needle=None):
        """Returns the contribution from needle-shaped precipitates to the
        shear stress in MPa using the model in Holmedal2015.

        Parameters
        ----------
        needle : sequence of str
            Name of all needle-shaped precipitates that should be
            included in this model.  Default from the
            `data_ppt_Holmedal2015_needle` attribute, which defaults
            to all phases.
        """
        chem = self.chem
        kappa = self.get_constant('ppt_Holmedal2015_kappa', self.kwargs)
        mu = self.get_constant('ppt_Holmedal2015_mu', self.kwargs)
        b = self.get_constant('Myhr2015_b' ,self.kwargs)
        #l0 = self.get_constant('ppt_Holmedal2015_l0', self.kwargs)
        ac = self.get_constant('ppt_Holmedal2015_ac', self.kwargs)

        if isinstance(needle, str):
            needle = [needle]
        elif needle is None:
            needle = self.get_constant('ppt_Holmedal2015_needle', self.kwargs)
        if needle is None:
            needle = set(chem.phasenames)
        mask = np.zeros((chem.ndomains, ), dtype=bool)
        for phase in needle:
            mask += chem.phasenames == phase
        Nd = chem.Nd[mask]
        r = chem.rd[mask]

        if np.allclose(chem.shape, 1):
            # aspect seems not to be given, derive it from: Omega = sqrt(5 * l)
            k = 0.190 * 1e-9
            V = 4 * pi / 3 * r ** 3
            l = sqrt( V / k )                  # precipitate lengths - Du et al 2016
            Omega = sqrt(5 * l)                # l / sqrt(cross section area)
        else:
            l = 2 * chem.shape ** (2/3) * r
            Omega = sqrt(3 / pi) * chem.shape

        Nv = np.sum(Nd)
        lmean = np.sum(l * Nd) / Nv
        a = (l / Omega) ** 2
        i1 = a < ac
        i2 = a >= ac
        fmean = 1 / (Nv * lmean) * (
            1 / ac**kappa * np.sum(
                (l ** (2 * kappa + 1) / Omega ** (2 * kappa) * Nd)[i1]) +
            np.sum((l * Nd)[i2]))
        # There is a misprint in Eq. 14 in Holmedal2015 which is corrected below
        return 0.3 * mu * b * sqrt(3 * sqrt(3) * lmean * Nv * fmean**3) * (
            1 - fmean**5 / 6)


    #-------------------------------------------------------------------------
    #  Dislocations (disl)
    #-------------------------------------------------------------------------
    def tau_disl_Myhr2015(self):
        """Returns the dislocation contribution to the shear stress
        in MPa using the model in Myhr2015."""
        b = self.get_constant('Myhr2015_b', self.kwargs)
        G = self.get_constant('Myhr2015_Gshear', self.kwargs)
        alpha = self.get_constant('disl_Myhr2016_alpha', self.kwargs)
        return alpha * G * b * np.sqrt(self.microstructure.rho_i)


    #-------------------------------------------------------------------------
    #  Grains and subgrains (grain)
    #-------------------------------------------------------------------------
    def tau_grain_Alflow(self):
        """Returns contribution (in MPa) to the shear stress from grains and
        subgrains."""
        b = self.get_constant('Myhr2015_b', self.kwargs)
        G = self.get_constant('Myhr2015_Gshear', self.kwargs)
        alpha2 = self.get_constant('grain_Alflow_alpha2', self.kwargs)
        m = self.microstructure
        return alpha2 * G * b * (1 / m.grainsize + 1 / m.delta)


