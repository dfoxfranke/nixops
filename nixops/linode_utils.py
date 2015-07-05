import os, threading, linode.api

_cacheLock = threading.RLock()
_keyConnCache = dict()
_fileKeyCache = dict()
_datacentersCache = None
_distributionsCache = None
_kernelsCache = None
_linodeplansCache = None
_nodebalancersCache = None
_stackscriptsCache = None

def get_apikey(keyfile=None):
    """Read and return the (possibly cached) contents keyfile (if given),
    otherwise return the value of the environment variable
    $LINODE_API_KEY (if defined), otherwise return None."""
    global _cacheLock, _fileKeyCache
    with _cacheLock:
        if keyfile:
            if keyfile in _fileKeyCache:
                key = _fileKeyCache[keyfile]
            else:
                with open(keyfile, 'r') as f:
                    key = f.read().strip()
                _fileKeyCache[keyfile] = key
            return key
        else:
            return os.environ.get("LINODE_API_KEY", None)

def purge_keyfile(keyfile=None):
    """Purge the cached contents of keyfile."""
    global _cacheLock, _fileKeyCache
    if not keyfile:
        return
    with _cacheLock:
        if keyfile in _fileKeyCache:
            del _fileKeyCache[keyfile]

def get_connection_by_key(key):
    """Return a (possibly cached) connection using the given API key."""
    global _cacheLock, _keyConnCache
    if not key:
        return None
    with _cacheLock:
        if key in _keyConnCache:
            conn = _keyConnCache[key]
        else:
            conn = linode.api.Api(key)
            _keyConnCache[key] = conn
        return conn

def purge_connection_by_key(key):
    global _cacheLock, _keyConnCache
    with _cacheLock:
        if key in _keyConnCache:
            del _keyConnCache[key]

def get_connection_by_keyfile(keyfile=None):
    global _cacheLock
    with _cacheLock:
        return get_connection_by_key(get_apikey(keyfile))
    
def purge_connection_by_keyfile(keyfile=None):
    global _cacheLock
    with _cacheLock:
        purge_connection_by_key(get_apikey(keyfile))
        purge_keyfile(keyfile)
        
def get_datacenters(conn):
    global _cacheLock, _datacentersCache
    with _cacheLock:
        if _datacentersCache is None:
            _datacentersCache = conn.avail.datacenters()
        return list(_datacentersCache)

def purge_datacenters():
    global _cacheLock, _datacentersCache    
    with _cacheLock:
        _datacentersCache = None

def get_distributions(conn):
    global _cacheLock, _distributionsCache
    with _cacheLock:
        if _distributionsCache is None:
            _distributionsCache = conn.avail.distributions()
        return list(_distributionsCache)

def purge_distributions():
    global _cacheLock, _distributionsCache
    with _cacheLock:
        _distributionsCache = None

def get_kernels(conn):
    global _cacheLock, _kernelsCache
    with _cacheLock:
        if _kernelsCache is None:
            _kernelsCache = conn.avail.kernels()
        return list(_kernelsCache)

def purge_kernels():
    global _cacheLock, _kernelsCache
    with _cacheLock:
        _kernelsCache = None

def get_linodeplans(conn):
    global _cacheLock, _linodeplansCache
    with _cacheLock:
        if _linodeplansCache is None:
            _linodeplansCache = conn.avail.linodeplans()
        return list(_linodeplansCache)

def purge_linodeplans():
    global _cacheLock, _linodeplansCache
    with _cacheLock:
        _linodeplansCache = None

def get_nodebalancers(conn):
    global _cacheLock, _nodebalancersCache
    with _cacheLock:
        if _nodebalancersCache is None:
            _nodebalancersCache = conn.avail.nodebalancers()
        return list(_nodebalancersCache)

def purge_nodebalancers():
    global _cacheLock, _nodebalancersCache
    with _cacheLock:
        _nodebalancersCache = None
        
def get_stackscripts(conn):
    global _cacheLock, _stackscriptsCache
    with _cacheLock:
        if _stackscriptsCache is None:
            _stackscriptsCache = conn.avail.stackscripts()
        return list(_stackscriptsCache)

def purge_stackscripts():
    global _cacheLock, _stackscriptsCache
    with _cacheLock:
        _stackscriptsCache = None
