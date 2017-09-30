#-*- coding: utf-8 -*-
#Vstream https://github.com/Kodi-vStream/venom-xbmc-addons
#usineagaz
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui 
from resources.lib.handler.inputParameterHandler import cInputParameterHandler 
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler 
from resources.lib.parser import cParser 
from resources.lib.util import cUtil
from resources.lib.config import cConfig
from resources.lib.handler.premiumHandler import cPremiumHandler
from resources.lib.gui.guiElement import cGuiElement 
from resources.lib.gui.contextElement import cContextElement
import xbmc,xbmcgui,urllib,urllib2,re,random,mimetypes,string

from resources.lib.config import GestionCookie

SITE_IDENTIFIER = 'siteuptobox2' 
SITE_NAME = '[COLOR dodgerblue]' + 'VotreCompteUptobox2' + '[/COLOR]'
SITE_DESC = 'fichier sur compte uptobox'
URL_MAIN = 'https://uptobox.com/'
BURL = 'https://uptobox.com/?op=my_files' 
UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
headers = { 'User-Agent' : UA }

def load(): 
    oGui = cGui()
    oPremiumHandler = cPremiumHandler('uptobox')
    
    if (cConfig().getSetting('hoster_uptobox_username') == '') and (cConfig().getSetting('hoster_uptobox_password') == ''):
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]'+ 'Nécessite Un Compte Uptobox Premium ou Gratuit' + '[/COLOR]')
    else:
        if (GestionCookie().Readcookie('uptobox') != ''):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
            oGui.addDir(SITE_IDENTIFIER, 'showFile', 'MesFichiers', 'genres.png', oOutputParameterHandler)
    
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://Dossier/')
            oGui.addDir(SITE_IDENTIFIER, 'showFolder', 'MesDossiers', 'genres.png', oOutputParameterHandler)
        else:
            Connection = oPremiumHandler.Authentificate()
            if (Connection == False):
                xbmcgui.Dialog().notification('Info connexion', 'Connexion refusé', xbmcgui.NOTIFICATION_ERROR,2000,False)
                return
                
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
            oGui.addDir(SITE_IDENTIFIER, 'showFile', 'MesFichiers', 'genres.png', oOutputParameterHandler)
    
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://Dossier/')
            oGui.addDir(SITE_IDENTIFIER, 'showFolder', 'MesDossiers', 'genres.png', oOutputParameterHandler)    
     

    oGui.setEndOfDirectory()
    
def showFile():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    if (oInputParameterHandler.exist('type')):
        sType = oInputParameterHandler.getValue('type')
    else:
        sType = 1
        
    oPremiumHandler = cPremiumHandler('uptobox')
    
    oParser = cParser()
    
    if 'uptobox.com' in sUrl:
        sHtmlContent = oPremiumHandler.GetHtml(sUrl)
        sHtmlContent = sHtmlContent.replace('class="blue_link">&nbsp;. .&nbsp; ()</a></td>','')
        
        sFolder = ''
        sName = ''
        sPattern = '<td class="tri">.+?<a href="([^"]+)" class="blue_link">(.+?)<\/a><\/td>'
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            for aEntry in aResult[1]:
                sFolder =  URL_MAIN + aEntry[0]
                sName = re.sub('[\(\[].+?[\)\]]','',aEntry[1])

                sName = cUtil().DecoTitle(sName) #deco saison et ep
                
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl',sFolder)
                oOutputParameterHandler.addParameter('type',sType)
                oOutputParameterHandler.addParameter('sFileName', sName)
                CreateFolder(oGui,sName,'showFile',oOutputParameterHandler)
    else:    
        sHtmlContent = oPremiumHandler.GetHtml(BURL)

    sPattern = '<td><a href="([^"]+)" class=".+?">([^<]+)<\/a>.+?<td>(.+?)<\/td>'
    aResult = oParser.parse(sHtmlContent, sPattern)  
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sHosterUrl = aEntry[0]
            sTitle = aEntry[1]
            sDisplayTitle = cUtil().DecoTitle(aEntry[1] + ' ' + '[' + aEntry[2] + ']')

            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                showHoster(oGui,oHoster,sHosterUrl,sTitle,sDisplayTitle,sType)

        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showFile', '[COLOR teal]Next >>>[/COLOR]', 'next.png', oOutputParameterHandler)
            
    oGui.setEndOfDirectory()
    
def __checkForNextPage(sHtmlContent):
    sPattern = "<a href='([^']+)'>(?:Next|Suivant).+?<\/a>"
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        return URL_MAIN + aResult[1][0]
 
    return False   
    
def showHoster(oGui,oHoster,sMediaUrl,sTitle,sDisplayTitle,sType):
    oGuiElement = cGuiElement()
    mTitle = sTitle
    ftitle = sTitle.lower()
    iliste = ['.mp4','.avi','.mkv','.mov','.wmv','.divx','xvid','.ts']
    for item in iliste:
        if item in ftitle:
           mTitle = ftitle.replace(item,'')
           
    if cConfig().getSetting("meta-view") == 'false':
       oGuiElement.setMetaAddon('true')        
       oGuiElement.setMeta(int(sType))
       
    oGuiElement.setSiteName('cHosterGui')
    oGuiElement.setFunction('play')
    oGuiElement.setTitle(sDisplayTitle)
    oGuiElement.setFileName(mTitle)
    oGuiElement.setIcon('host.png')

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('sMediaUrl', sMediaUrl)
    oOutputParameterHandler.addParameter('sHosterIdentifier','uptobox')
    oOutputParameterHandler.addParameter('sFileName',sTitle)
    oOutputParameterHandler.addParameter('sTitle', sDisplayTitle)
    oOutputParameterHandler.addParameter('sId', 'cHosterGui')
    oOutputParameterHandler.addParameter('siteUrl', sMediaUrl)

    #my menu
    if (oHoster.isDownloadable() == True):
        oContext = cContextElement()
        oContext.setFile(SITE_IDENTIFIER)
        oContext.setSiteName(SITE_IDENTIFIER)
        oContext.setFunction('Rename')
        oContext.setTitle('Renommer')
        oContext.setOutputParameterHandler(oOutputParameterHandler)
        oGuiElement.addContextItem(oContext)
        
    oGui.createContexMenuWatch(oGuiElement, oOutputParameterHandler) 
    
    #Download menu
    if (oHoster.isDownloadable() == True):
        oContext = cContextElement()
        oContext.setFile('cDownload')
        oContext.setSiteName('cDownload')
        oContext.setFunction('AddtoDownloadList')
        oContext.setTitle(cConfig().getlanguage(30202))
        oContext.setOutputParameterHandler(oOutputParameterHandler)
        oGuiElement.addContextItem(oContext)
            
    if (oHoster.isDownloadable() == True):
        #Beta context download and view menu
        oContext = cContextElement()
        oContext.setFile('cDownload')
        oContext.setSiteName('cDownload')
        oContext.setFunction('AddtoDownloadListandview')
        oContext.setTitle('DL et Visualiser')
        oContext.setOutputParameterHandler(oOutputParameterHandler)
        oGuiElement.addContextItem(oContext) 
        
    #context FAV menu
    oGui.createContexMenuFav(oGuiElement, oOutputParameterHandler)
        
    #context Library menu
    #oGui.CreateSimpleMenu(oGuiElement,oOutputParameterHandler,'cLibrary','cLibrary','setLibrary','[COLOR teal]Ajouter a la librairie[/COLOR]')  
    
    oGui.addHost(oGuiElement, oOutputParameterHandler)
      
def CreateFolder(oGui,sTitle,sFunction,oOutputParameterHandler):
    oInputParameterHandler = cInputParameterHandler()
    sType = oInputParameterHandler.getValue('type')

    oGuiElement = cGuiElement()

    if cConfig().getSetting("meta-view") == 'false':
       oGuiElement.setMetaAddon('true')
       
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction(sFunction)
    oGuiElement.setTitle(sTitle)
    oGuiElement.setFileName(sTitle)
    oGuiElement.setIcon("genres.png")
    oGuiElement.setMeta(int(sType))

    #my menu
    oContext = cContextElement()
    oContext.setFile(SITE_IDENTIFIER)
    oContext.setSiteName(SITE_IDENTIFIER)
    oContext.setFunction('Rename')
    oContext.setTitle('Renommer')
    oContext.setOutputParameterHandler(oOutputParameterHandler)
    oGuiElement.addContextItem(oContext)
    
    oGui.addFolder(oGuiElement,oOutputParameterHandler)

def showFolder():
    oGui = cGui()
    oPremiumHandler = cPremiumHandler('uptobox')

    sHtmlContent = oPremiumHandler.GetHtml(BURL)
    
    oParser = cParser()
    sPattern = '<td class="tri">.+?<a href="([^"]+)" class="blue_link">(.+?)<\/a><\/td>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog,total)
            if dialog.iscanceled():
                break

            sTitle = re.sub('[\(\[].+?[\)\]]','',aEntry[1])
            sUrl = aEntry[0]
            if not sUrl.startswith('https'):
               sUrl = 'https://uptobox.com/' + sUrl
               
            sTitle = cUtil().DecoTitle(sTitle) #deco saison et ep
            
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl',sUrl) 
            
            name = cUtil().CleanName(sTitle) #nettoie le titre

            if 'film' in name:
                oOutputParameterHandler.addParameter('type',1)
                oOutputParameterHandler.addParameter('sFileName', name)
                CreateFolder(oGui,sTitle,'showFile',oOutputParameterHandler)
                #xbmc.log('---------------------------------------film')
            elif 'serie' in name:
                oOutputParameterHandler.addParameter('type',2)
                oOutputParameterHandler.addParameter('sFileName', name)
                CreateFolder(oGui,sTitle,'showFile',oOutputParameterHandler)
                #xbmc.log('--------------------------------------serie')
            else:
                oOutputParameterHandler.addParameter('type',3)#chinte pas de meta
                oOutputParameterHandler.addParameter('sFileName', name)
                CreateFolder(oGui,sTitle,'showFile',oOutputParameterHandler) 
                #xbmc.log('--------------------------------------autre') 

                
        cConfig().finishDialog(dialog)
        
    oGui.setEndOfDirectory()
    
#Renomme dossiers et fichiers 
def Rename():
    #voir public ou privée
    oInputParameterHandler = cInputParameterHandler() 

    aParams = oInputParameterHandler.getAllParameter()
    sTitle = oInputParameterHandler.getValue('sFileName')
    #sTitle = sTitle.replace('.mp4','')
    xbmc.log(str(aParams))
    sUrl = oInputParameterHandler.getValue('siteUrl')
    
    sText = cConfig().showKeyBoard(sTitle) 
    if sText == False:
       return
       
    post_data = {}
    
    if 'fld_id=' in sUrl:
        sId = sUrl.replace('https://uptobox.com/?op=my_files&fld_id=','').replace('http://uptobox.com/?op=my_files&fld_id=','')
        sUrl = 'http://uptobox.com/?op=fld_edit&fld_id=' + sId
        
        post_data['op'] = 'fld_edit'
        post_data['fld_id'] = sId
        post_data['fld_name'] = sText 
        post_data['save'] = 'Soumettre' 
        
    else:
        sId = sUrl.replace('https://uptobox.com/','').replace('http://uptobox.com/','')
        sUrl = 'https://uptobox.com/?op=file_edit&file_code=' + sId
        
        post_data['op'] = 'file_edit'
        post_data['file_code'] = sId
        post_data['file_name'] = sText 
        post_data['save'] = 'Soumettre' 
        
    oPremiumHandler = cPremiumHandler('uptobox')
    cookies = GestionCookie().Readcookie('uptobox')

    req = urllib2.Request(sUrl,urllib.urlencode(post_data),headers)
    req.add_header('Cookie', cookies)
    try:
        rep = urllib2.urlopen(req)
    except:
        return ''

    rep.close()
    
    xbmc.executebuiltin("Container.Refresh")
    
def AddmyAccount():
    if (cConfig().getSetting('hoster_uptobox_username') == '') and (cConfig().getSetting('hoster_uptobox_password') == ''):
        return 
    oInputParameterHandler = cInputParameterHandler()
    sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')

    sId = sMediaUrl.replace('https://uptobox.com/','').replace('http://uptobox.com/','')

    Upurl = 'https://uptobox.com/?op=my_files&add_my_acc=' + sId

    oPremiumHandler = cPremiumHandler('uptobox')
    if (GestionCookie().Readcookie('uptobox') != ''):

        cookies = GestionCookie().Readcookie('uptobox')
        sHtmlContent = oPremiumHandler.GetHtmlwithcookies(Upurl,None,cookies)
        if (len(sHtmlContent) > 25):

            oPremiumHandler.Authentificate()
            cookies = GestionCookie().Readcookie('uptobox')
            sHtmlContent = oPremiumHandler.GetHtmlwithcookies(Upurl,None,cookies)

    else:
        sHtmlContent = oPremiumHandler.GetHtml(Upurl)
        
    xbmc.executebuiltin("Dialog.Close(all,true)") 
    if ('dded to your account' in sHtmlContent):
        xbmcgui.Dialog().notification('Info upload','Fichier ajouté à votre compte',xbmcgui.NOTIFICATION_INFO,2000,False)      
    elif ('nvalid file' in sHtmlContent):
        xbmcgui.Dialog().notification('Info upload','Fichier introuvable',xbmcgui.NOTIFICATION_INFO,2000,False)
    else:
        xbmcgui.Dialog().notification('Info upload','Erreur',xbmcgui.NOTIFICATION_ERROR,2000,False)    

def UptomyAccount():
    if (cConfig().getSetting('hoster_uptobox_username') == '') and (cConfig().getSetting('hoster_uptobox_password') == ''):
        return 
    oInputParameterHandler = cInputParameterHandler()
    sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')

    oPremiumHandler = cPremiumHandler('uptobox')

    sHtmlContent = oPremiumHandler.GetHtml(URL_MAIN)
    cookies = GestionCookie().Readcookie('uptobox')
  
    aResult = re.search('<div id="div_url".+?action="([^"]+)".+?name="sess_id" value="([^"]+)".+?name="srv_tmp_url" value="([^"]+)"',sHtmlContent,re.DOTALL)
    if (aResult):
        aCt = aResult.group(1)
        sId = aResult.group(2)
        sTmp = aResult.group(3)

        UPurl = ('%s%s&js_on=1&utype=reg&upload_type=url' % (aCt,sId))
 
        fields = {'sess_id':sId,'upload_type':'url','srv_tmp_url':sTmp,'url_mass':sMediaUrl,'tos':'1','submit_btn':'Uploader'}
        mpartdata = MPencode(fields)
        req = urllib2.Request(UPurl,mpartdata[1],headers)
        req.add_header('Content-Type', mpartdata[0])
        req.add_header('Cookie', cookies)
        req.add_header('Content-Length', len(mpartdata[1]))
        #req.add_data(mpartdata[1])
        xbmcgui.Dialog().notification('Info upload', 'Envoi de la requete patienter ..', xbmcgui.NOTIFICATION_INFO,2000,False)
        try:
           rep = urllib2.urlopen(req)
        except:
            return ''

        sHtmlContent = rep.read()
        rep.close()
        xbmc.executebuiltin("Dialog.Close(all,true)")
        if '>OK<' in sHtmlContent:
           xbmcgui.Dialog().notification('Info upload', 'Upload réussie', xbmcgui.NOTIFICATION_INFO,2000,False)
        else:
           xbmcgui.Dialog().notification('Info upload', 'Fichier introuvable', xbmcgui.NOTIFICATION_INFO,2000,False)
    else:
        xbmcgui.Dialog().notification('Info upload','Erreur pattern',xbmcgui.NOTIFICATION_ERROR,2000,False)
        
def MPencode(fields):
	random_boundary = __randy_boundary()
	content_type = "multipart/form-data, boundary=%s" % random_boundary

	form_data = []
	
	if fields:
		for (key, value) in fields.iteritems():
			if not hasattr(value, 'read'):
				itemstr = '--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (random_boundary, key, value)
				form_data.append(itemstr)
			elif hasattr(value, 'read'):
				with value:
					file_mimetype = mimetypes.guess_type(value.name)[0] if mimetypes.guess_type(value.name)[0] else 'application/octet-stream'
					itemstr = '--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: %s\r\n\r\n%s\r\n' % (random_boundary, key, value.name, file_mimetype, value.read())
				form_data.append(itemstr)
			else:
				raise Exception(value, 'Field is neither a file handle or any other decodable type.')
	else:
		pass

	form_data.append('--%s--\r\n' % random_boundary)

	return content_type, ''.join(form_data)

def __randy_boundary(length=10,reshuffle=False):
	character_string = string.letters+string.digits
	boundary_string = []
	for i in range(0,length):
		rand_index = random.randint(0,len(character_string) - 1)
		boundary_string.append(character_string[rand_index])
	if reshuffle:
		random.shuffle(boundary_string)
	else:
		pass
	return ''.join(boundary_string)        
