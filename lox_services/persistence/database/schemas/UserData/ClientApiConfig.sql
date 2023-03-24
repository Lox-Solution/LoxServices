UserData.ClientApiConfig
(
  company STRING NOT NULL, --REQUIRED
  connection STRING OPTIONS(description="Status of API connection"),
  curl_request STRING OPTIONS(description="Demo request made in curl"),
  documentation_url STRING OPTIONS(description="Documentation on how to handle the clients API."),
  contact_person STRING OPTIONS(description="Email of the user that requested the API setup."),
  insert_datetime DATETIME NOT NULL, --REQUIRED
  update_datetime DATETIME
)
