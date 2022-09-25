<div align='center'>
  <img src="./assets/torpy.png">
</div>


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
```
