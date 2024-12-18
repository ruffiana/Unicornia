# Lovense Cog
Redbot cog for controlling Lovense toys on a Discord server.

## Installation
1. Get your developer token from the [Lovense developer dashboard](https://developer.lovense.com/).
2. Setup the callback URL to the URL or Publi IP address of the web server.

## Reference:
[Lovense standar API](https://developer.lovense.com/docs/standard-solutions/standard-api.html#by-local-application)

1. Your server calls Lovense server's API (use POST request)
```
"https://api.lovense-api.com/api/lan/getQrCode",
  {
    token: "your developer token", // Lovense developer token
    uid: "11111", // user ID on your website
    uname: "user name", // user nickname on your website
    utoken: md5(uid + "salt"), // This is for your own verification purposes. We suggest you to generate a unique token/secret for each user. This allows you to verify the user and avoid others faking the calls.
    v: 2,
  }
```
2. You will get:
```
{
   code: 0
   message: "Success"
   result: true
   data: {
     "qr": "https://test2.lovense.com/UploadFiles/qr/20220106/xxx.jpg", // QR code picture
     "code": "xxxxxx"
   }
}
```
3. Once the user scans the QR code with the Lovense Remote app, the app will invoke the Callback URL you've provided in the developer dashboard. The Lovense server is no longer required. All communications will go from the app to your server directly.
4. The Lovense Remote app will send the following POST to your server:
```{
  "uid": "xxx",
  "appVersion": "4.0.3",
  "toys": {
    "xxxx": {
      "nickName": "",
      "name": "max",
      "id": "xxxx",
      "status": 1
    }
  },
  "wssPort": "34568",
  "httpPort": "34567",
  "wsPort": "34567",
  "appType": "remote",
  "domain": "192-168-1-44.lovense.club",
  "utoken": "xxxxxx",
  "httpsPort": "34568",
  "version": "101",
  "platform": "android"
}
```

## Testing WebServer and port
### Internal:
`curl -X POST -H "Content-Type: application/json" -d "{\"key\": \"value\"}" http://localhost:8000`
### External:
`curl -X POST -H "Content-Type: application/json" -d "{\"key\": \"value\"}" [External_IP]:8000`