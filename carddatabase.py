# -*- coding: utf-8 -*-

import md5
import os
import urllib
import urllib2
import re
import lxml.etree

CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cache')

class CardDatabase(object):
	LAND_TO_GATHERER_ID = {
		'forest': '174928',
		'swamp': '197258',
		'island': '190588',
		'plains': '197255',
		'mountain': '190586',
	}
	
	def __init__(self):
		self.cache = []
		
	def __del__(self):
		import os
		
		for path in self.cache:
			os.remove(path)
			
	def online_lookup(self, query):
		query = str(query)
		gatherer_id = re.compile(r'\d+')
		
		if not gatherer_id.match(query):
			if query.lower() in CardDatabase.LAND_TO_GATHERER_ID.keys():
				return self.online_lookup(CardDatabase.LAND_TO_GATHERER_ID[query.lower()])
			else:
				return self.online_lookup_by_name(query)
		else:
			return self.online_lookup_by_id(query)
			
	def _check_for_cached_query(self, query):
		cached_filename = query + repr(self)
		cached_filename = md5.new(cached_filename).hexdigest() + '.txt'
		
		global CACHE_PATH
		if not os.path.exists(CACHE_PATH):
			os.makedirs(CACHE_PATH)
			
		cached_file = os.path.join(CACHE_PATH, cached_filename)
		if cached_file in self.cache:
			return open(cached_file, 'r')
		return None
		
	def _get_response_object(self, url):
		request = urllib2.Request(url=url)
		request.add_header('user-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv.1.8.1.4) Gecko/20070515 Firefox/2.0.0.4')
		xml = urllib2.urlopen(request)
		
		return xml
		
	def online_lookup_by_name(self, name):
		cached_file = self._check_for_cached_query(name)
		if cached_file is None:
			url = "http://gatherer.wizards.com/pages/search/default.aspx?"
			url = url + urllib.urlencode([('name', '["' + name + '"]'),])
		
			xml = self._get_response_object(url)
		
			cached_filename = name + repr(self)
			cached_filename = md5.new(cached_filename).hexdigest() + '.txt'
		
			cached_filename = os.path.join(CACHE_PATH, cached_filename)
			f = open(cached_filename, 'w')
			f.write(xml.read())
			f.close()
			
			self.cache.append(cached_filename)
			
			cached_file = open(cached_filename, 'r')
		
		return self._parse_gatherer_xml(cached_file)
		
	def online_lookup_by_id(self, gatherer_id):
		cached_file = self._check_for_cached_query(gatherer_id)
		if cached_file is None:
			url = "http://gatherer.wizards.com/Pages/Card/Details.aspx?"
			url = url + urllib.urlencode([('multiverseid', gatherer_id),])
		
			xml = self._get_response_object(url)
		
			cached_filename = name + repr(self)
			cached_filename = md5.new(cached_filename).hexdigest() + '.txt'
		
			cached_filename = os.path.join(CACHE_PATH, cached_filename)
			f = open(cached_filename, 'w')
			f.write(xml.read())
			f.close()
			
			self.cache.append(cached_filename)
			
			cached_file = open(cached_filename, 'r')
		
		return self._parse_gatherer_xml(cached_file)
		
	def _parse_gatherer_xml(self, xml):
		parser = lxml.etree.XMLParser(recover=True)
		tree = lxml.etree.parse(xml, parser)
		
		gatherer_id_regex = re.compile(r'\?multiverseid=(\d*)$')
		name_regex = re.compile(r'nameRow$')
		
		card_data = {}
		
		form = tree.findall("//{http://www.w3.org/1999/xhtml}form")[0]
		card_data['gatherer_id'] = gatherer_id_regex.search(form.get('action')).group(1)
		
		for div in tree.findall("//{http://www.w3.org/1999/xhtml}div"):
			div_id = div.get('id')
			
			if div_id is not None:
				if name_regex.search(div_id):
					card_data['name'] = div.getchildren()[1].text.strip() 
		
		return card_data
		
if __name__ == '__main__':
	db = CardDatabase()
	print db.online_lookup('Tolsimir Wolfblood')