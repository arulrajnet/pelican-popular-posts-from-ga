Popular Posts from Google Analytics
----------------------------------------------------

Popular posts based on number of views from Google Analytics. 

## Setup

#### Install Dependencies

```
sudo pip install --upgrade google-api-python-client
```

#### pelicanconf.py

* Setup Google API https://console.developers.google.com/iam-admin/serviceaccounts/serviceaccounts-zero
* Create new project
* Create new service account
* Download json key file (not p12) for that service account. You have to use this file in pelicanconf.py `GOOGLE_OAUTH_KEY_FILE`
* Now goto analytics Admin section https://analytics.google.com/analytics/web/#management/Settings
* Under User management add earlier created service account mail id init.

More Info on https://developers.google.com/analytics/devguides/reporting/core/v3/quickstart/service-py

```
# Pelican Plugin path
 PLUGIN_PATHS = [
   '/folder/path/of/where/is/plugin/repo/'
 ]

# Plugins used
PLUGINS = [
  'pelican-popular-posts-from-ga'
 ]
 
# Analytics
GOOGLE_ANALYTICS = "UA-XXXXXX-X"
GOOGLE_OAUTH_KEY_FILE = "/full/path/of/google/service/account/json/file"
```


## Usage

```
{% if GOOGLE_OAUTH_KEY_FILE %}
   <div class="sidebar">
           <h2>Popular posts</h2>
           <ul>
           {% for article in popular_posts %}
                <li>
                  <a href="{{ SITEURL }}/{{ article.url }}">{{ article.title }}</a>
                <section>
                    <p>
                    {% if article.has_summary %}
                        {{ article.summary }}
                    {% elif article.summary %}
                        {{ article.summary|striptags|truncate(250) }}
                    {% endif %}
                    </p>
                </section>
                </li>
           {% endfor %}
           </ul>
   </div>
{% endif %}

```

Now it default popular post of last 10 days.

## TODO

* Support for popular posts by user defined days from pelicanconf.py
* Support for popular posts by category / tags.

