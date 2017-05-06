"""
Python interface for TeVCat (http://tevcat.uchicago.edu/)
"""

import urllib
import base64
import tempfile
import json
from astropy.coordinates import SkyCoord, Angle
from astropy import units as u
import pkg_resources
import math
import numpy

observatory_names = {1:  'Whipple',
                     2:  'Telescope Array',
                     3:  'HEGRA',
                     5:  'CANGAROO',
                     6:  'H.E.S.S.',
                     7:  'MAGIC',
                     8:  'Milagro',
                     9:  'Durham',
                     10: 'Crimea',
                     14: 'VERITAS',
                     15: 'Potchefstroom',
                     19: 'ARGO-YBJ',
                     22: 'HAWC'}

source_type_names = {1:  'HBL',
                     7:  'DARK',
                     8:  'FRI',
                     10: 'LBL',
                     13: 'PSR',
                     14: 'PWN',
                     16: 'Shell',
                     17: 'Starburst',
                     18: 'UNID',
                     21: 'XRB',
                     22: 'Cat. Var.',
                     24: 'FSRQ',
                     25: 'IBL',
                     27: 'Gamma BIN',
                     29: 'SNR/Molec. Cloud',
                     30: 'Massive Star Cluster',
                     31: 'AGN (unknown type)',
                     32: 'Star Forming Region',
                     33: 'Globular Cluster',
                     34: 'BL Lac (class unclear)',
                     35: 'Binary',
                     36: 'Composite SNR',
                     37: 'Blazar',
                     38: 'Superbubble'}

def p(a, b):
    return a[0:b]


class TeVCat(object):
    def __init__(self):
        """
        Initialize database by downloading HTML data from the TeVCat home page
        """
        url = 'http://tevcat.uchicago.edu/'
        tmp = tempfile.NamedTemporaryFile()
        urllib.urlretrieve(url, tmp.name)
        f = open(tmp.name)
        for line in f.readlines():
            if line.find('Version') >= 0:
                self.version = line.split()[-1]
            elif line.find('var dat  =') >= 0:
                data = line.split('"')[1]
            elif line.find('pytevcat') >= 0:
                lim = int(line.split('pytevcat = ')[1].split(';')[0])

        self.json = json.loads(base64.b64decode(data[0:lim]))

        self.sources = []
        for i in range(len(self.json[u'sources'])):
            self.sources.append(Source(self.json[u'sources'][i], self))
        self.catalogs = {}
        for key in self.json[u'catalogs'].keys():
            self.catalogs[int(key)] = Catalog(self.json[u'catalogs'][key])

    def getCatalog(self, i):
        """
        Returns a catalog.
        """
        return self.catalogs[i]

    def getSources(self):
        """
        Returns the list of sources.
        """
        return self.sources

class Catalog(object):
    def __init__(self, catalog):
        self.id          = int(catalog[u'id'])
        self.description = str(catalog[u'description'])
        self.role_id     = str(catalog[u'role_id']) # for what? always -1
        self.public      = str(catalog[u'public']) # for what? always 1
        self.name        = str(catalog[u'name'])

    def getID(self):
        """
        Returns the ID number of the catalog.
        """
        return self.id

    def getDescription(self):
        """
        Returns the description of the catalog.
        """
        return self.description

    def getName(self):
        """
        Returns the name of the catalog.
        """
        return self.name

    def __str__(self):
        s = ''
        s += 'Name:\t%s\n' % self.getName()
        s += 'Description:\t%s' % self.getDescription()

        return s

class Source(object):
    def __init__(self, source, tevcat):
        """
        Initialize source parameters with JSON data
        """
        self.tevcat = tevcat
        
        self.observatory_name = str(source[u'observatory_name'])
        if self.observatory_name not in observatory_names.values():
            print 'Unknown observatory name found: ', self.observatory_name

        self.discoverer = int(source[u'discoverer'])
        try:
            if observatory_names[self.discoverer] != self.observatory_name:
                print '"discoverer" (%d) does not match with "observatory_name" (%s)' % (self.discoverer, self.observatory_name)
        except:
            raise BaseException('Cannot find discoverer "%s" (%d)' % (self.observatory_name, self.discoverer))
            
        self.variability = None if source[u'variability'] == None else int(source[u'variability'])
        if self.variability not in (None, 0, 1, 2):
            print 'Unknown variability type found'

        self.image = str(source[u'image']) # No use. URL of marker

        self.size_x = 0. if source[u'size_x'] == None else float(source[u'size_x'])
        self.size_y = 0. if source[u'size_y'] == None else float(source[u'size_y'])

        self.owner = None if source[u'owner'] == None else int(source[u'owner']) # for what?
        if self.owner not in (None, 1, 2):
            print 'Unknown owner type found'

        self.id = int(source[u'id'])

        self.discovery_date = None if source[u'discovery_date'] == None else int(source[u'discovery_date'].replace('/', ''))
        if self.discovery_date != None and ((not (1 <= self.discovery_date%100 <= 12)) or not (1987 <= self.discovery_date/100 <= 2020)):
            print 'Invalid date format found: %d' % self.discovery_date

        self.other_names = source[u'other_names']

        self.canonical_name = str(source[u'canonical_name'])

        self.marker_id = source[u'marker_id'] # No use? always None

        self.public = int(source[u'public']) # No use? always 1

        self.spec_idx = None if source[u'spec_idx'] == None else float(source[u'spec_idx'])

        self.private_notes = source[u'private_notes']

        self.catalog_name = str(source[u'catalog_name']) # in format of TeV JXXXX+/-XXX

        self.greens_cat = str(source[u'greens_cat']) # Green's cagalog

        self.source_type = int(source[u'source_type'])

        self.src_rank = None if source[u'src_rank'] == None else int(source[u'src_rank']) # for what?

        self.coord_type = source[u'coord_type'] # No use? always null or 0

        self.source_type_name = str(source[u'source_type_name'])
        if self.source_type_name not in source_type_names.values():
            print 'Unknown source type name found: ', self.source_type_name
        if source_type_names[self.source_type] != self.source_type_name:
            print '"source_type" (%d) does not match with "source_type_name" (%s)' % (self.source_type, self.source_type_name)

        self.distance = None if source[u'distance'] == None else float(source[u'distance'])

        coord_ra  = source[u'coord_ra']
        coord_dec = source[u'coord_dec']
        if coord_ra[-1] == ' ':
            coord_ra = coord_ra[:-1]
        if coord_dec[-1] == ' ':
            coord_dec = coord_dec[:-1]
        hms, dms = str(coord_ra.replace(' ', ':')), str(coord_dec.replace(' ', ':'))
        self.fk5 = SkyCoord(hms + ' ' + dms, frame='fk5', unit=(u.hourangle, u.deg))
        self.galactic = self.getPosition().transform_to('galactic')
        self.glon = self.galactic.l
        self.glat = self.galactic.b

        self.notes = source[u'notes']

        self.distance_mod = None if source[u'distance_mod'] == None else str(source[u'distance_mod'])
        if self.distance_mod not in (None, 'z', 'kpc'):
            print 'Unknown distance mode found: ', self.distance_mod

        self.flux = None if source[u'flux'] == None else float(source[u'flux'])
        
        self.ext = bool(int(source[u'ext']))

        self.catalog_id = int(source[u'catalog_id'])

        self.eth = None if source[u'eth'] == None else float(source[u'eth'])

    def getObservatoryName(self):
        """
        Returns the name of the observatory which first detected the source.
        """
        return self.observatory_name

    def getDiscoverer(self):
        """
        Returns the observatory ID which corresponds the observatory name.
        """
        return self.discoverer

    def isVariable(self):
        """
        Returns True if the source is variable.
        """
        if self.variability == None:
            return False
        else:
            return True

    def getVariability(self):
        """
        Returns the variability of the source.
        """
        return self.variability

    def getSize(self):
        """
        Returns the size of the source.
        """
        return self.size_x, self.size_y

    def getOwner(self):
        return self.owner

    def getID(self):
        """
        Returns the source ID number.
        """
        return self.id

    def getDiscoveryDate(self):
        """
        Returns the date of discovery (yyyy, mm).
        """
        if self.discovery_date != None:
            return self.discovery_date/100, self.discovery_date%100
        else:
            return None

    def getOtherNames(self):
        """
        Returns other names of the source.
        """
        return self.other_names

    def getCanonicalName(self):
        return self.canonical_name

    def getSpectralIndex(self):
        """
        Returns the spectral index of the source.
        """
        return self.spec_idx

    def getPrivateNotes(self):
        """
        Returns the private notes on the source.
        """
        return self.private_notes

    def getCatalogName(self):
        """
        Returns the catalog name (TeV J...) of the source.
        """
        return self.catalog_name

    def getGreensCatalog(self):
        """
        Returns the URL of the corresponding Green's catalog.
        """
        return self.greens_cat

    def getSourceType(self):
        """
        Returns the type of the source.
        """
        return self.source_type

    def getSourceTypeName(self):
        """
        Returns the name of the typeof the source.
        """
        return self.source_type_name

    def getDistance(self):
        """
        Returns the distance and its unit of the source.
        """
        return self.distance, self.distance_mod

    def getPosition(self):
        """
        Returns the celestial position of the source.
        """
        return self.fk5

    def getICRS(self):
        """
        Returns ICRS coordinates
        """
        icrs = self.getPosition().transform_to('icrs')
        return icrs

    def getFK5(self):
        """
        Returns FK5 coordinates (J2000)
        """
        return self.getPosition()

    def getFK4(self):
        """
        Returns FK4 coordinates (B1950)
        """
        fk4 = self.getPosition().transform_to('fk4')
        return fk4

    def getGalactic(self):
        """
        Returns Galactic coordinates
        """
        return self.galactic

    def getHMSDMS(self):
        """
        Returns (RA, Dec) of the source in (HH:MM:SS, DD:MM:SS) format (J2000)
        """
        return self.getPosition().to_string('hmsdms')

    def getNotes(self):
        """
        Returns the notes on the source.
        """
        return self.notes

    def getFlux(self):
        """
        Returns the flux of the source in Crab unit.
        """
        return self.flux

    def isExtended(self):
        """
        Retruns True if the source is extended one.
        """
        return self.ext

    def getCatalog(self):
        """
        Returns the catalog in which the source is registered.
        """
        return self.getTeVCat().getCatalog(self.catalog_id)

    def getEnergyThreshold(self):
        """
        Returns the energy threshold of the source (GeV).
        """
        return self.eth

    def getTeVCat(self):
        """
        Returns TeVCat object
        """
        return self.tevcat

    def __str__(self):
        """
        Returns summary of the source in the TeVCat format
        See e.g. http://tevcat.uchicago.edu/?mode=1&showsrc=100
        """
        s = ''
        s += 'Canonical Name:\t%s\n' % self.getCanonicalName()
        s += 'TeVCat Name:\t%s\n' % self.getCatalogName()
        s += 'Other Names:\t%s\n' % self.getOtherNames()
        s += 'Source Type:\t%s\n' % self.getSourceTypeName()
        s += 'RA:\t%s (hh mm ss)\n' % self.getHMSDMS().split()[0]
        s += 'Dec:\t%s (dd mm ss)\n' % self.getHMSDMS().split()[1]
        s += 'Gal Long:\t%.2f (deg)\n' % self.getGalactic().l.degree
        s += 'Gal Lat:\t%.2f (deg)\n' % self.getGalactic().b.degree
        dist = self.getDistance()
        if dist[1] == 'z':
            s += 'Distance:\tz = %f\n' % dist[0]
        elif dist[1] == 'kpc':
            s += 'Distance:\t%f kpc\n' % dist[0]
        else:
            s += 'Distance:\n'

        if self.getFlux() == None:
            s += 'Flux:\n'
        else:
            s += 'Flux:\t%.03f (Crab Units)\n' % self.getFlux()

        if self.getEnergyThreshold() != None:
            s += 'Energy Threshold:\t%d (GeV)\n' % self.getEnergyThreshold()
        else:
            s += 'Energy Threshold:\n'

        s += 'Size (X):\t%.2f (deg)\n' % self.getSize()[0]
        s += 'Size (Y):\t%.2f (deg)\n' % self.getSize()[1]

        if self.getDiscoveryDate() != None:
            s += 'Discovery Date:\t%04d-%02d\n' % self.getDiscoveryDate()
        else:
            s += 'Discovery Date:\n'

        s += 'Discovered by:\t%s' % self.getObservatoryName()

        return s

try:
    import ROOT
    rad2deg = ROOT.TMath.RadToDeg()
    deg2rad = ROOT.TMath.DegToRad()
except:
    pass
else:
    import __main__
    class Viewer(ROOT.TGMainFrame):
        def __init__(self):
            ROOT.TGMainFrame.__init__(self, 0, 10, 10, ROOT.kHorizontalFrame)
            self.tevcat = TeVCat()

            self.xsize = 1440
            self.ysize = 720
            self.subsize = 300

            self.controls = ROOT.TGVerticalFrame(self)
            self.AddFrame(self.controls, ROOT.TGLayoutHints(ROOT.kLHintsRight | ROOT.kLHintsExpandY, 5, 5, 5, 5))

            self.main_dispatch = ROOT.TPyDispatcher(self.main_update)

            # sub canvas
            self.subCanvas = ROOT.TRootEmbeddedCanvas('subCanvas', self.controls, self.subsize, self.subsize)
            self.subCanvas.GetCanvas().SetMargin(0, 0, 0, 0)
            self.controls.AddFrame(self.subCanvas, ROOT.TGLayoutHints(ROOT.kLHintsExpandX))

            # Source Info
            self.info = ROOT.TGTextView(self.controls)
            self.controls.AddFrame(self.info, ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY))

            self.search_dispatch = ROOT.TPyDispatcher(self.sources_update)
            
            # Search Box
            self.search_frame = ROOT.TGHorizontalFrame(self.controls)
            self.controls.AddFrame(self.search_frame, ROOT.TGLayoutHints(ROOT.kLHintsExpandX))
            self.search_label = ROOT.TGLabel(self.search_frame, 'Search  ')
            self.search_frame.AddFrame(self.search_label, ROOT.TGLayoutHints(ROOT.kLHintsCenterY))
            self.search_box = ROOT.TGTextEntry(self.search_frame)
            self.search_frame.AddFrame(self.search_box, ROOT.TGLayoutHints(ROOT.kLHintsCenterY | ROOT.kLHintsExpandX))
            self.search_box.Connect("TextChanged(char*)", "TPyDispatcher", self.search_dispatch, "Dispatch()")

            # Enable/disable the LAT all-sky image
            self.name_group = ROOT.TGGroupFrame(self.controls, "Source Name Labels")
            self.name_group.SetTitlePos(ROOT.TGGroupFrame.kCenter)
            self.name = ROOT.TGCheckButton(self.name_group, "Show/Hide")
            self.name.SetOn(0)
            self.name_group.AddFrame(self.name, ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY))
            self.controls.AddFrame(self.name_group, ROOT.TGLayoutHints(ROOT.kLHintsExpandX))
            self.name.Connect("Toggled(Bool_t)", "TPyDispatcher", self.main_dispatch, "Dispatch()")

            # Enable/disable the LAT all-sky image
            self.lat_group = ROOT.TGGroupFrame(self.controls, "LAT All-sky Image")
            self.lat_group.SetTitlePos(ROOT.TGGroupFrame.kCenter)
            self.lat = ROOT.TGCheckButton(self.lat_group, "Show/Hide")
            self.lat.SetOn()
            self.lat_group.AddFrame(self.lat, ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY))
            self.controls.AddFrame(self.lat_group, ROOT.TGLayoutHints(ROOT.kLHintsExpandX))
            self.lat.Connect("Toggled(Bool_t)", "TPyDispatcher", self.main_dispatch, "Dispatch()")

            # Color
            self.color = ROOT.TGButtonGroup(self.controls, "LAT Image Color")
            self.lat.Connect("Toggled(Bool_t)", "TGButtonGroup", self.color, "SetState(Bool_t)")
            self.color.SetTitlePos(ROOT.TGGroupFrame.kCenter)
            self.colorButton = (ROOT.TGRadioButton(self.color, "Color", 0),
                                ROOT.TGRadioButton(self.color, "Gray Scale (B to W)", 1),
                                ROOT.TGRadioButton(self.color, "Gray Scale (W to B)", 2))
            self.color.SetButton(0)
            self.controls.AddFrame(self.color, ROOT.TGLayoutHints(ROOT.kLHintsExpandX))
            self.color.Connect("Pressed(Int_t)", "TPyDispatcher", self.main_dispatch, "Dispatch(Long_t)")

            self.contents = ROOT.TGHorizontalFrame(self)
            self.AddFrame(self.contents, ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY))

            # Enable/disable the LAT all-sky image
            self.cat_group = ROOT.TGGroupFrame(self.controls, "Catalog")
            self.cat_group.SetTitlePos(ROOT.TGGroupFrame.kCenter)
            self.cat_check = [ROOT.TGCheckButton(self.cat_group, "Default Catalog"),
                              ROOT.TGCheckButton(self.cat_group, "Newly Announced"),
                              ROOT.TGCheckButton(self.cat_group, "Other Sources"),
                              ROOT.TGCheckButton(self.cat_group, "Source Candidates")]
            for i in range(len(self.cat_check)):
                if i < 2:
                    self.cat_check[i].SetOn()
                self.cat_check[i].Connect("Toggled(Bool_t)", "TPyDispatcher", self.main_dispatch, "Dispatch()")
                self.cat_group.AddFrame(self.cat_check[i], ROOT.TGLayoutHints(ROOT.kLHintsExpandX | ROOT.kLHintsExpandY))
            self.controls.AddFrame(self.cat_group, ROOT.TGLayoutHints(ROOT.kLHintsExpandX))

            # main canvas
            self.mainCanvas = ROOT.TRootEmbeddedCanvas('mainCanvas', self.contents, self.xsize + 4, self.ysize + 4)
            self.mainCanvas.GetCanvas().SetMargin(0, 0, 0, 0)
            self.contents.AddFrame(self.mainCanvas, ROOT.TGLayoutHints(ROOT.kLHintsCenterX | ROOT.kLHintsCenterY))

            __main__.tevcatDummyGlobalFunction = self.sub_update

            self.mainCanvas.GetCanvas().AddExec('dynamic', 'TPython::Exec("tevcatDummyGlobalFunction()");')
            self.mainCanvas.GetCanvas().Update()

            self.SetWindowName('TeVCat Viewer')
            self.MapSubwindows()
            self.Resize()
            self.MapWindow()
            self.MapRaised()

            self.main_update(0)

        def sub_update(self):
            self.subCanvas.GetCanvas().Clear()
            self.subCanvas.GetCanvas().cd()
                                    
            if self.sub_image != None:
                px = int(self.mainCanvas.GetCanvas().GetEventX())
                py = int(self.ysize - self.mainCanvas.GetCanvas().GetEventY())
                self.info_update(px, py)
                
                if px - self.subsize/8 >= 0 and py - self.subsize/8 >= 0:
                    self.sub_image.Zoom(px - self.subsize/8, py - self.subsize/8, self.subsize/4, self.subsize/4)
                self.sub_image.SetEditable(1)
                self.sub_image.Draw()

                self.subCanvas.GetCanvas().Range((px - self.subsize/8 + 0.)/self.xsize,
                                                 (py - self.subsize/8 + 0.)/self.ysize,
                                                 (px + self.subsize/8 + 0.)/self.xsize,
                                                 (py + self.subsize/8 + 0.)/self.ysize)
                
                try:
                    for gra in self.graphs.values():
                        gra.Draw('p same')
                except:
                    pass

                try:
                    for name in self.source_names_large:
                        name.Draw()
                except:
                    pass

                self.subCanvas.GetCanvas().Update()

        def main_update(self, button = 100):
            self.mainCanvas.GetCanvas().Clear()
            self.mainCanvas.GetCanvas().cd()

            if self.lat.IsOn():
                if button == 0 or (button == 100 and self.color.GetButton(0).IsOn()):
                    fname = pkg_resources.resource_filename("tevcat", "img/allsky_b.png")
                    self.image = ROOT.TImage.Open(fname)
                    self.sub_image = ROOT.TImage.Open(fname)
                    self.grid_color = 0
                elif button == 1 or (button == 100 and self.color.GetButton(1).IsOn()):
                    fname = pkg_resources.resource_filename("tevcat", "img/allsky_gray.png")
                    self.image = ROOT.TImage.Open(fname)
                    self.sub_image = ROOT.TImage.Open(fname)
                    self.grid_color = 0
                elif button == 2 or (button == 100 and self.color.GetButton(2).IsOn()):
                    fname = pkg_resources.resource_filename("tevcat", "img/allsky_gray_inv.png")
                    self.image = ROOT.TImage.Open(fname)
                    self.sub_image = ROOT.TImage.Open(fname)
                    self.grid_color = 1

                self.image.SetEditable(1)
                self.image.Draw()
            else:
                self.color.SetState(False)
                self.image = None
                self.sub_image = None

            # Draw coordinate grids
            self.grid = []
            for l in range(-180, 181, 30):
                self.grid.append(ROOT.TPolyLine())
                for b in range(-90, 91, 2):
                    x, y = self.sky2pad(l, b)
                    self.grid[-1].SetNextPoint(x, y)
                self.grid[-1].Draw()

            for b in range(-60, 61, 30):
                self.grid.append(ROOT.TPolyLine())
                for l in range(-180, 181, 2):
                    x, y = self.sky2pad(l, b)
                    self.grid[-1].SetNextPoint(x, y)

            for grid in self.grid:
                grid.SetLineStyle(2)
                grid.SetLineColor(self.grid_color)
                grid.Draw()

            # Draw grid labels
            self.label = [ROOT.TLatex(0.975, 0.5, '-180#circ'),
                          ROOT.TLatex(0.025, 0.5, '+180#circ'),
                          ROOT.TLatex(0.5, 0.98, '+90#circ'),
                          ROOT.TLatex(0.5, 0.02, '-90#circ')]
            for label in self.label:
                label.SetTextAlign(22)
                label.SetTextSize(0.03)
                label.Draw()

            self.copyright = ROOT.TLatex(0.99, 0.01, 'TeVCat Ver. %s' % self.tevcat.version)
            self.copyright.SetTextAlign(31)
            self.copyright.SetTextSize(0.03)
            self.copyright.Draw()

            self.sources_update()

        def sources_update(self):
            # Draw sources
            self.graphs = {}
            self.source_names = []
            self.source_names_large = []
            
            search = self.search_box.GetText().lower()

            for source in self.tevcat.getSources():
                useThisSource = None
                for i in range(len(self.cat_check)):
                    if self.cat_check[i].IsOn() and source.getCatalog().getName() == self.cat_check[i].GetTitle():
                        useThisSource = True
                        break

                if source.__str__().lower().find(search) < 0:
                    continue

                if not useThisSource:
                    continue

                gal = source.getGalactic()
                x, y = self.sky2pad(gal.l.degree, gal.b.degree)
                source_type_name = source.getSourceTypeName()
                try:
                    self.graphs[source_type_name]
                except:
                    self.graphs[source_type_name] = ROOT.TGraph()
                    self.graphs[source_type_name].SetEditable(0)
                graph = self.graphs[source_type_name]
                graph.SetPoint(graph.GetN(), x, y)
                graph.Draw('p same')

                # Draw source Names
                if self.name.IsOn():
                    self.source_names.append(ROOT.TText(x, y, '  %s' % source.getCanonicalName()))
                    self.source_names[-1].SetTextAngle(45)
                    self.source_names[-1].SetTextColor(self.grid_color)
                    self.source_names[-1].SetTextSize(0.015)
                    self.source_names[-1].SetTextAlign(12)
                    self.source_names[-1].Draw()
                    self.source_names_large.append(self.source_names[-1].Clone())
                    self.source_names_large[-1].SetTextSize(0.06)

            for i, gra in enumerate(self.graphs.values()):
                gra.SetMarkerColor(i/4 + 2)                
                gra.SetMarkerStyle(20 + i%10)
                gra.SetMarkerSize(1)

            # Draw legend
            self.legend = ROOT.TLegend(0., 0., 0.22, 0.18)
            self.legend.SetNColumns(2)
            self.legend.SetBorderSize(0)
            self.legend.SetFillStyle(0)
            self.legend.SetLineStyle(0)
            for source_type in self.graphs.keys():
                self.legend.AddEntry(self.graphs[source_type], source_type, 'p')
            self.legend.Draw()

            ROOT.gPad.Modified()
            ROOT.gPad.Update()

        def info_update(self, px, py):
            """
            """
            try:
                lb = self.pad2sky((px + .5)/self.xsize, (py + .5)/self.ysize)
            except:
                return
            if lb == None:
                return

            nearby_source = None
            minimum_angsep = Angle(180*u.deg)

            search = self.search_box.GetText().lower()

            sources = []
            cursor_pos = SkyCoord(lb[0], lb[1], frame='galactic', unit='deg')

            for source in self.tevcat.getSources():
                useThisSource = None
                for i in range(len(self.cat_check)):
                    if self.cat_check[i].IsOn() and source.getCatalog().getName() == self.cat_check[i].GetTitle():
                        useThisSource = True
                        break

                if source.__str__().lower().find(search) < 0:
                    continue

                sources.append(source)

            pos = SkyCoord(l=[s.glon for s in sources], b=[s.glat for s in sources], frame='galactic')
            angsep = pos.separation(cursor_pos)
            degs = angsep.degree
            i = numpy.argmin(degs)
            minimum_angsep = degs[i]
            nearby_source = sources[i]
                
            if minimum_angsep > 3.:
                self.info.SetText(ROOT.TGText(""))
                return

            text = ROOT.TGText('')
            info = nearby_source.__str__().replace(u'\xb0', u'') # another candidate?
            info = str(info.replace(u'\u2212', u'-').replace(u'\u2013', u'-'))
            
            for i, line in enumerate(info.split('\n')):
                text.InsLine(i, line)
            self.info.SetText(text)
            self.info.Update()

        def pad2sky(self, x, y):
            c = 1.4142135623730951*2./math.pi
            x_ = -((x - (1. - c)/2.)/c*4. - 2.)
            y_ = (y - (1. - c)/2.)*2./c - 1.

            gamma = (2. - (x_/2.)**2 - y_**2)**-0.5
            theta = math.asin(y_/gamma)
            phi = math.asin(x_/(2.*gamma*math.cos(theta)))*2.
            
            if abs(x_) > 2.*math.cos(theta) or abs(y_) > 1.:
                return None

            l = phi*rad2deg
            b = theta*rad2deg
            
            return (l, b)
            
        def sky2pad(self, l, b):
            while l > 180.:
                l -= 360

            theta = b*deg2rad
            phi   = l*deg2rad
            gamma = (1 + math.cos(theta)*math.cos(phi/2.))**-0.5
            x_ = 2*gamma*math.cos(theta)*math.sin(phi/2.)
            y_ = gamma*math.sin(theta)

            # CDELT1 = -0.25
            # CDELT2 = +0.25
            # AITOFF
            # NAXIS1 = 1440
            # NAXIS2 = 720
            c = 1.4142135623730951*2/math.pi
            y = (y_ + 1)/2.*c + (1 - c)/2.
            x = (-x_ + 2)/4.*c + (1 - c)/2.
            return x, y
