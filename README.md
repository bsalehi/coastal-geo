# coastal-geo

This is a geolocation demo. 

Input: can be a twitter account or a piece of a text. 

Outputs:
1) The predicted location based on user's network
2) The predicted location based on text-based model proposed by Rahimi et al., 2016 (pigeo: A Python Geotagging Tool)
3) The most location indicative words based on KL divergence scores
4) The most location indicative words based on entropy scores
5) The predicted location based on textual data is shown on a map
6) The next most probable predicted locations are listed under the map


Requires:
Python
3 saved files/models shared at https://www.dropbox.com/sh/sgsfd7fgusnux1i/AADwxQtzQDcIrL_lTR5TEMdpa?dl=0
 

How to run?
1) download and extract the three files shared at dropbox (link above)
2) get token access to twitter and fill the following variables in start.py
   access_token = ""
    access_token_secret = ""
    consumer_key = ""
    consumer_secret = ""
3) run start.py






