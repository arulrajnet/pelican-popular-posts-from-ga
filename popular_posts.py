# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from pelican import signals
from pelican import ArticlesGenerator

try:
  from apiclient.discovery import build
  from oauth2client.service_account import ServiceAccountCredentials

  import httplib2
  from oauth2client import client
  from oauth2client import file
  from oauth2client import tools
except:
  logger.warning('`popular_posts` failed to load dependency `google-api-python-client`.'
                 '`popular_posts` plugin not loaded.')


class SetupGoogleAnalyticsError(Exception):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return repr(self.message)


class FetchGoogleAnalyticsError(Exception):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return repr(self.message)


class GoogleAnalyticsService(object):

  json_key_file_path = None
  property_ids = None
  analytics_service = None

  """docstring for GoogleAnalyticsService"""

  def __init__(self, json_key_file_path, analytics_code):
    super(GoogleAnalyticsService, self).__init__()
    if json_key_file_path is None or len(json_key_file_path.strip()) is 0 or analytics_code is None or len(
        analytics_code.strip()) is 0:
      raise SetupGoogleAnalyticsError("Google oauth key file or google analytics id can't be empty or None.")
    self.json_key_file_path = json_key_file_path
    self.analytics_service = self.__analytics_service__(json_key_file_path)
    if self.analytics_service is None:
      raise SetupGoogleAnalyticsError("The given key file is not valid.")

    try:
      self.analytics_service.management().accounts().list().execute()
    except Exception as e:
      raise SetupGoogleAnalyticsError("The service account mail id not mapped with analytics.")

    self.property_ids = self.__get_analytics_profile__(self.analytics_service, analytics_code)
    if len(self.property_ids) is 0:
      raise SetupGoogleAnalyticsError("The given %s id is not available." % analytics_code)

  def __google_service__(self, api_name, api_version, scope, json_key_file):
    """Get a service that communicates to a Google API.

    Args:
      api_name: The name of the api to connect to.
      api_version: The api version to connect to.
      scope: A list auth scopes to authorize for the application.
      key_file_location: The path to a valid service account json file.

    Returns:
      A service that is connected to the specified API.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scopes=scope)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    service = build(api_name, api_version, http=http)

    return service

  def __analytics_service__(self, json_key_file):
    scope = ['https://www.googleapis.com/auth/analytics.readonly']
    api_name = "analytics"
    api_version = "v3"
    return self.__google_service__(api_name=api_name, api_version=api_version, scope=scope, json_key_file=json_key_file)

  def __get_analytics_profile__(self, service, analytics_code):
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    profileIds = []
    for account in accounts.get('items'):
      # Get the first Google Analytics account.
      accountId = account.get('id')

      # Get a list of all the properties for the first account.
      properties = service.management().webproperties().list(
        accountId=accountId).execute()

      for property in properties.get('items'):
        # print "Property %s " % property

        # Get the first property id.
        propertyId = property.get('id')

        if propertyId == analytics_code:
          # Get a list of all views (profiles) for the property.
          profiles = service.management().profiles().list(
            accountId=accountId,
            webPropertyId=propertyId).execute()

          for profile in profiles.get('items'):
            # return the first view (profile) id.
            profileIds.append(profile.get('id'))

    return profileIds

  def popular_pages(self, number_of_days):
    return self.analytics_service.data().ga().get(
      ids='ga:' + self.property_ids[0], start_date=str(number_of_days) + 'daysAgo',
      end_date='today', max_results=10, metrics='ga:pageviews',
      sort='-ga:pageviews',
      dimensions='ga:pagePath').execute()


def init_ga(generator):
  if "GOOGLE_OAUTH_KEY_FILE" in generator.settings.keys() and "GOOGLE_ANALYTICS" in generator.settings.keys():
    key_file_json = generator.settings["GOOGLE_OAUTH_KEY_FILE"]
    analytics_code = generator.settings["GOOGLE_ANALYTICS"]
    try:
      gas = GoogleAnalyticsService(key_file_json, analytics_code)
      generator.popular_posts_plugin_instance = gas
    except Exception as e:
      print e
    finally:
      pass
  else:
    raise SetupGoogleAnalyticsError("GOOGLE_OAUTH_KEY_FILE or GOOGLE_ANALYTICS not set.")


def get_popular_pages(generators):
  article_generator = None

  for generator in generators:
    if type(generator) == ArticlesGenerator:
      article_generator = generator

  popular_posts = []
  if hasattr(article_generator, "popular_posts_plugin_instance"):
    results = article_generator.popular_posts_plugin_instance.popular_pages(10)
    if results and results.get('rows'):
      for row in results.get('rows'):
        if row and len(row) > 1:
          for article in article_generator.articles:
            if row[0] == '/' + article.url:
              popular_posts.append(article)

  article_generator.context['popular_posts'] = popular_posts


def register():
  """
      Plugin registration
  """
  try:
    signals.article_generator_init.connect(init_ga)
    signals.all_generators_finalized.connect(get_popular_pages)
  except ImportError:
    logger.warning('`popular_posts` failed to load dependency `google-api-python-client`.'
                   '`popular_posts` plugin not loaded.')
