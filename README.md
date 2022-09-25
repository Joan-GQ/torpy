<div align='center'>
  <img src="./assets/torpy.png">
</div>

Torpy is a custom library for anonymizing HTTP requests using ![Tor](https://www.torproject.org/) as a proxy. It provides methods similar to the ones found in the ![`requests`](https://pypi.org/project/requests) package. The Onion class is actually a wrapper for the `requests.Session` object.

# Requirements:

- **Linux based OS**
- **Tor installed as service**: It can be installed by running the following command in Linux
```console
sudo apt-get install tor
```
- `requests` package with Sockets installed too. You can get it by:
```console
pip install requests[socks]
```
- All the libraries on `src/tor.py`

# Example usage

```python
import tor

# Initialize Onion service
onion = tor.Onion()

# Get TOR session IP
print(onion.get_ip())
# >>> 123.456.78.12 [Example IP, returns actual TOR session IP]

# Make a HTTP GET request to a custom URL
request = onion.get('https://www.wikipedia.org')
print(request.text)
# >>> [The webpage as text]

# Get new identity
onion.renew_identity()
print(onion.get_ip())
# >>> 255.123.45.67 [Example IP, should return a different valid TOR session IP]
```
