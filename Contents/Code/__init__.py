import urllib, re, time, random

TITLE    	= 'RedTube'
PREFIX   	= '/video/redtube'
randomArt 	= random.randint(1,4)
ART 		= 'artwork-'+str(randomArt)+'.jpg'
#ART      	= 'artwork-2.jpg'
ICON     	= 'icon-default.png'
SEARCH_ICON = 'icon-search.png'

##My notes:  functions called as callbacks really dont' work well with default parms.  Various clients (like Home Theater) don't process that well and end up with managed variables
APISEARCH_URL = 	'http://api.redtube.com/?data=redtube.Videos.searchVideos&%s&thumbsize=big&output=json'

REDTUBE_APIBASE 				= 'http://api.redtube.com/?data=redtube.Videos.searchVideos&%s&thumbsize=big&output=json'
REDTUBE_ORDERED 				= (REDTUBE_APIBASE % ('ordering=%s&period=%s'))

REDTUBE_BASE					= 'http://api.redtube.com'	#todo:fixup use of this
REDTUBE_NEWEST 					= (REDTUBE_APIBASE % ('ordering=newest&page=%s'))
REDTUBE_RATED 					= (REDTUBE_APIBASE % ('ordering=rating&period=%s&page=%s'))
REDTUBE_VIEWED 					= (REDTUBE_APIBASE % ('ordering=mostviewed&period=%s&page=%s'))
REDTUBE_CHANNELS_LIST_HTML		= 'http://www.redtube.com/channels'
REDTUBE_CHANNELS_LIST			= 'http://api.redtube.com/?data=redtube.Categories.getCategoriesList&output=json'
REDTUBE_CHANNELS				= (REDTUBE_APIBASE % ('category=%s&ordering=%s&page=%s'))			#(searchQuery, sortOrder, str(page)))
REDTUBE_TAGS_LIST				= 'http://api.redtube.com/?data=redtube.Tags.getTagList&output=json'
REDTUBE_TAGS					= (REDTUBE_APIBASE % ('tags[]=%s%s&page=%s'))			#(searchQuery, [sortOrder], str(page)))
REDTUBE_PORNSTARS_LIST			= 'http://api.redtube.com/?data=redtube.Stars.getStarDetailedList&output=json'	#list of every pornstar with thumbnail
REDTUBE_PORNSTAR 				= (REDTUBE_APIBASE % ('stars[]=%s&page=%s'))		#(searchQuery, str(page))
REDTUBE_SEARCH					= (REDTUBE_APIBASE % ('search=%s%s&page=%s'))		#(searchQuery , '&ordering='+sortOrder,  str(page)))

#TODO: Figure out messed up foreign characters and HTML type tags in names

PAGE_SIZE 						= int(20)	#REDTUBE API page size is 20
PORNSTAR_PAGE_SIZE 				= int(30)	#we can define the size of the list so use a bigger list then 20
####################################################################################################

def Start():
	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)

	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	EpisodeObject.thumb = R(ICON)
	EpisodeObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)

###################################################################################################
# This tells Plex how to list you in the available channels and what type of channels this is 
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
	# You have to open an object container to produce the icons you want to appear on this page. 
	oc = ObjectContainer()
	oc.add(DirectoryObject(key=Callback(MovieList, mainTitle='Newest', url=REDTUBE_NEWEST), title='Newest', summary='The newest RedTube vidoes', thumb=R(ICON)))
	oc.add(PopupDirectoryObject(key=Callback(SortOrderSubMenu, mainTitle='Top Rated', url=REDTUBE_RATED), title='Top Rated', summary='See the Top Rated RedTube videos', thumb=R(ICON)))
	oc.add(PopupDirectoryObject(key=Callback(SortOrderSubMenu, mainTitle='Most Viewed', url=REDTUBE_VIEWED), title='Most Viewed', summary='See the Most ViewedRedTube videos',  thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(CategoriesMenu), title='Categories', summary='Browse videos by category', thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(TagsMenu), title='Tags', summary='Browse videos by their tags', thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(PornstarsMenu), title='Porn Stars',summary='Find videos by your favorite porn star', thumb=R(ICON)))

	oc.add(InputDirectoryObject(key=Callback(Search), title="Search", summary="Search RedTube for videos", prompt="Search for", thumb=R(SEARCH_ICON)))
	#dir.Append(Function(DirectoryItem(FavoriteVideos, L('Favorites'))))
	return oc

	
####################################################################################################

##def Thumb(url):
##	try:
##		data = HTTP.Request(url).content
##		return DataObject(data, 'image/jpeg')
##	except:
##		return Redirect(R(ICON))

def GetDurationFromstr(duration):
	try:
		durationArray = duration.split(":")
		if len(durationArray) == 3:
			hours = int(durationArray[0])
			minutes = int(durationArray[1])
			seconds = int(durationArray[2])
		elif len(durationArray) == 2:
			hours = 0
			minutes = int(durationArray[0])
			seconds = int(durationArray[1])
		elif len(durationArray)	==	1:
			hours = 0
			minutes = 0
			seconds = int(durationArray[0])
		return int(((hours)*3600 + (minutes*60) + seconds)*1000)
	except:
		return 0

def msToRuntime(ms):
	if ms is None or ms <= 0:
		return None
	ret = []
	sec = int(ms/1000) % 60
	min = int(ms/1000/60) % 60
	hr  = int(ms/1000/60/60)
	return "%02d:%02d:%02d" % (hr,min,sec)


####################################################################################################
@route(PREFIX + '/categoriesmenu')
def CategoriesMenu():
	oc = ObjectContainer(title2='Category')
	pageFormat = 'channels'
	#HTML Version gets the thumbnails which is cool.  
	pageContent = HTML.ElementFromURL(REDTUBE_CHANNELS_LIST_HTML)
	for categoryItem in pageContent.xpath('//ul[@class="videoThumbs"]/li'):
		categoryItemTitle = categoryItem.xpath('div/a')[0].get('title')
		categoryItemCatName = categoryItem.xpath('div/a/img')[0].get('id')
		categoryItemThumb = categoryItem.xpath('div/a/img')[0].get('src')
		oc.add(DirectoryObject(key=Callback(SortOrderSubMenu, mainTitle=categoryItemTitle, url=REDTUBE_CHANNELS, searchQuery=categoryItemCatName, pageFormat=pageFormat), title=categoryItemTitle, thumb=categoryItemThumb))
	#Check to make sure we got all the Channels.  #japanesecensored doesn't show up in Web Page so just ignore it and make sure we're within 1 category of API
	categories = JSON.ObjectFromURL(REDTUBE_CHANNELS_LIST)
	if (len(oc) < len(categories['categories'])-1) or (len(oc) > len(categories['categories'])):	
		#fallback to using API version. API version is fastest and will not break if the web site changes but doesn't get thumbnails or pretty names
		oc = ObjectContainer(title2='Category')	#recreate oc object
		for key in categories['categories']:
			categoryItemTitle = key['category']
			categoryItemCatName = key['category']
			oc.add(DirectoryObject(key=Callback(SortOrderSubMenu, mainTitle=categoryItemTitle, url=REDTUBE_CHANNELS, searchQuery=categoryItemCatName, pageFormat=pageFormat), title=categoryItemTitle))
		
	return oc

@route(PREFIX + '/tagsmenu')
def TagsMenu():
	oc = ObjectContainer(title2='Tags')
	pageFormat = 'tags'
	tags = JSON.ObjectFromURL(REDTUBE_TAGS_LIST)
	for key in tags['tags']:
		tagName = key['tag']['tag_name']
		oc.add(DirectoryObject(key=Callback(SortOrderSubMenu, mainTitle=tagName, url=REDTUBE_TAGS, searchQuery=tagName, pageFormat=pageFormat), title=tagName))
		
	return oc

@route(PREFIX + '/pornstarsmenu')
def PornstarsMenu():
	oc = ObjectContainer(title2 = 'Porn Stars')
	availAlphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

	oc.add(DirectoryObject(key=Callback(PornstarsList, mainTitle='All', searchQuery='all'), title='All'))
	for alphabetItem in availAlphabet:
		oc.add(DirectoryObject(key=Callback(PornstarsList, mainTitle=alphabetItem.capitalize(), searchQuery=alphabetItem), title=alphabetItem.capitalize()))
	return oc

#filter the pornstars list.  
@route(PREFIX + '/pornstarsfilter')
def PornstarsListFilter(stars, searchQuery='x'):
	stars['stars'] = [value for value in stars['stars'] if value['star']['star_name'].lower().startswith(str(searchQuery))]
	#The enumeration method looks like it's faster on Intel hardware but so ugly!
	#array = stars['stars']
	#newArray = []
	#for (i, star) in enumerate(array):
	#	if star['star']['star_name'].lower().startswith(searchQuery):
	#	    newArray.append(star)
	#stars['stars'] = newArray
	return stars

@route(PREFIX + '/pornstarslist', page=int)
def PornstarsList(mainTitle,searchQuery,sortOrder='newest',page=1):
	oc = ObjectContainer(title2 = 'Porn Stars : ' + mainTitle)
	stars = JSON.ObjectFromURL(REDTUBE_PORNSTARS_LIST)
	start 	= (int(page)-1) * PORNSTAR_PAGE_SIZE
	pageFormat = 'pornstars'
	if 'stars' in stars:	#make sure there was a result
		if searchQuery != 'all':
			stars = PornstarsListFilter(stars, searchQuery)
		for x in range (start, start + PORNSTAR_PAGE_SIZE):
			if x >= len(stars['stars']):
					break
			star = stars['stars'][int(x)]
			if not 'star' in star:
				break
			else:
				star = star['star']
			pornstarItemTitle = star['star_name']
			pornstarItemThumb = star['star_thumb']
			pornstarItemQuery = star['star_url'].rsplit('/',1)[1].strip()
			oc.add(DirectoryObject(key=Callback(MovieList, url=REDTUBE_PORNSTAR, mainTitle=pornstarItemTitle, searchQuery=pornstarItemQuery, pageFormat=pageFormat, sortOrder=sortOrder), title=pornstarItemTitle, thumb=pornstarItemThumb))
	if len(oc) == PORNSTAR_PAGE_SIZE:
		oc.add(NextPageObject(key=Callback(PornstarsList, mainTitle=mainTitle, searchQuery=searchQuery, sortOrder=sortOrder, page=int(page)+1), title='more'))
	return oc

@route(PREFIX + '/sortordersubmenu')
def SortOrderSubMenu(url,mainTitle,searchQuery='none',pageFormat='normal'):
	oc = ObjectContainer(title2=mainTitle, no_cache=True)
	if pageFormat == 'channels':
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='newest'), title='Newest'))
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='rating'), title='Top Rated'))
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='mostviewed'), title='Most Viewed'))
		#oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='mostfavored'), title='Most Favored'))
	elif pageFormat == 'tags':
		#oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='default'), title='Most Relevant'))	#having no ordered is same as Newest
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='newest'), title='Newest'))
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='rating'), title='Top Rated'))
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='mostviewed'), title='Most Viewed'))
	elif pageFormat == 'search':
		#oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='default'), title='Most Relevant'))	#having no ordered is same as Newest
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='newest'), title='Newest'))
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='rating'), title='Top Rated'))
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='mostviewed'), title='Most Viewed'))
	else:
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='weekly'), title='Weekly'))
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='monthly'), title='Monthly'))
		oc.add(DirectoryObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='alltime'), title='All Time'))
	return oc

@route(PREFIX + '/movielist', page=int)
def MovieList(url, mainTitle='',searchQuery='none',pageFormat='normal',sortOrder='newest', page=1):
	if pageFormat == 'channels':
		videos = JSON.ObjectFromURL(url % (searchQuery, sortOrder, str(page)))
	elif pageFormat == 'tags':
		if sortOrder == 'default':
			videos = JSON.ObjectFromURL(url % (searchQuery, '', str(page)))		
		else:
			videos = JSON.ObjectFromURL(url % (searchQuery, '&ordering='+sortOrder, str(page)))		
	elif pageFormat == 'pornstars':
		videos = JSON.ObjectFromURL(url % (searchQuery, str(page)))
	elif pageFormat == 'search':
		if sortOrder == 'default':
			videos = JSON.ObjectFromURL(url % (searchQuery, '',  str(page)))
		else:
			videos = JSON.ObjectFromURL(url % (searchQuery , '&ordering='+sortOrder,  str(page)))

	else:
		try:
			videos = JSON.ObjectFromURL(url % (sortOrder, str(page)))
		except:
			videos = JSON.ObjectFromURL(url % (str(page)))
	if 'count' in videos:
		pageTotal = int(((int(videos['count'])+PAGE_SIZE-1)/PAGE_SIZE))
		oc = ObjectContainer(title2 = mainTitle + ' | Page: '+str(page) + ' / ' + str(pageTotal)) #, no_cache=True 
	else:
		oc = ObjectContainer(title2 = mainTitle + ' | Page: '+str(page), no_cache=True)

	# Enter a for loop to run through all data sets of the type data
	if 'videos' in videos:	#make sure there was a result
		for data in videos['videos']:
			#basically copied from the existing url service code
			if not 'video' in data:
				break
			else:
				data = data['video']

			title = data['title']
			vidurl = data['url']
			thumb = data['default_thumb'] #.replace('m.jpg', 'b.jpg')

			try: duration = TimeToMs(data['duration'])
			except: duration = None

			try: rating = float(data['rating']) * 2
			except: rating = None

			summary = ''		#fake a summary that is just the tag names
			tags = []
			if 'tags' in data:
				for key in data['tags']:
					tags.append(key['tag_name'])
					if summary <> '' :
						summary = summary + ','
					summary = summary + key['tag_name']

			try: originally_available_at = Datetime.ParseDate(data['publish_date']).date()
			except: originally_available_at = None

			try: year = int(data['publish_date'].split('-')[0])
			except: year = None

			oc.add(VideoClipObject(
				url = vidurl, 
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),
				summary = summary,
				rating = rating,
				tags = tags,
				duration = duration,
				year = year,
				content_rating_age = 18,
				originally_available_at = originally_available_at))
	if len(oc) < 1:
		#Log ('still no value for objects')
		return ObjectContainer(header=TITLE, message="No more videos found.", title2=mainTitle, no_cache=True)
	elif len(oc) == PAGE_SIZE:
		oc.add(NextPageObject(key=Callback(MovieList, url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder=sortOrder, page=(page+1)), title='more'))
	return oc


####################################################################################################
##def AddVideoToFavorites(sender,id,title,url,thumb):
##	favs = {}
##	if Data.Exists('favoritevideos'):
##		favs = Data.LoadObject('favoritevideos')
##		if id in favs:
##			return MessageContainer('Already a Favorite', 'This Video is already on your list of Favorites.')
##	favs[id] = [id, title, url, thumb]
##	Data.SaveObject('favoritevideos', favs)
##	return MessageContainer('Added to Favorites', 'This Video has been added to your Favorites.')
##
##def RemoveVideoFromFavorites(sender,id):
##	favs = Data.LoadObject('favoritevideos')
##	if id in favs:
##		del favs[id]
##		Data.SaveObject('favoritevideos', favs)
##		return MessageContainer('Removed from Favorites', 'This Video has been removed from your Favorites.')
##
##def FavoriteVideos(sender):
##	dir = MediaContainer(viewMode = "List", title2 = 'Favorites', noCache=True)
##	favs = Data.LoadObject('favoritevideos')
##	values = favs.values()
##	output = [(f[1], f[0], f[2], f[3]) for f in values]
##	output.sort()
##	for title, id, url, thumb in output:
##		dir.Append(Function(PopupDirectoryItem(FavoritesSubMenu, title=title, thumb=Function(Thumb, url=thumb)), id=id, title=title, url=url, thumb=thumb))
##	return dir
##
##def FavoritesSubMenu(sender,id,title,url,thumb):
##	dir = MediaContainer()
##	dir.Append(Function(VideoItem(PlayVideo,L('Play Video')), url=url))
##	dir.Append(Function(DirectoryItem(RemoveVideoFromFavorites, L('Remove from Favorites'), ''), id=id))
##	return dir
####################################################################################################

@route(PREFIX + '/search')
def Search(query):
	try:
		oc = SortOrderSubMenu(REDTUBE_SEARCH,'Search Results', searchQuery=String.Quote(query, usePlus=True),pageFormat='search')
		return oc
	except:
		return ObjectContainer(header=TITLE, message="No search results found", no_cache=True)

####################################################################################################


#Never gets called.  No idea why.  Is it in the URL service?
@route(PREFIX + '/setrating')
def SetRating(key,rating):
	Log(key+" - "+str(rating))

#############################################################################################################################
# This is a function to pull the thumb from a the head of a page
@route(PREFIX + '/getthumb')
def GetThumb(url):
	page = HTML.ElementFromURL(url)
	try:
		thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
		if not thumb.startswith('http://'):
			thumb = http + thumb
	except:
		thumb = R(ICON)
	return thumb
