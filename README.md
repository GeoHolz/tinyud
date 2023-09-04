<p align="center">
  <img src="images/tinyud.png" />
</p>

# tinyud

Tiny Up & Down is a simple python program that alerts you via Gotify when a service is unavailable.
<p align="center">
  <img src="images/example.jpg" width="25%" >
</p>

## Installation

Simply download the tinyud.py file


## Configuration

First, you need to specify your Gotify address and token in the database ( BDD tinydb.json will be created ) :
```bash
python3 tinyud.py --add --name GotifyURL --address https://YOU_URL_TO_GOTIFY/message?token=YOUR_TOKEN
```
Then add your services to be monitored one by one :
```bash
python3 tinyud.py --add --name Service1 --address 192.168.0.1
```

To list all services :
```bash
python3 tinyud.py --list
```

To delete a service :
```bash
python3 tinyud.py --delete --name Name_Of_Service
```
## Usage
Use cron to schedule an automatic program start, for example every 5 minutes: 

```bash
5 * * * * python3 tinyud.py >/dev/null 2>&1
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)