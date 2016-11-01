
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.util import redirectTo, Redirect
from twisted.web.resource import Resource
from twisted.python.filepath import FilePath

from lae_site.handlers.emailcollector import CollectEmailHandler
from lae_site.handlers.web import JinjaHandler
from lae_site.handlers.submit_subscription import SubmitSubscriptionHandler

from lae_site import __file__ as _lae_root

_CONTENT = FilePath(_lae_root).parent().sibling("content")

def make_site(email_path, stripe_api_key, service_confirmed_path, subscriptions_path, site_logs_path):
    resource = JinjaHandler('index.html')
    resource.putChild('static', File(_CONTENT.child(b"static").path))
    resource.putChild('blog', File(_CONTENT.child(b"blog").path))
    resource.putChild('collect-email', CollectEmailHandler(email_path))
    resource.putChild('signup', Redirect("/"))
    resource.putChild('submit-subscription', SubmitSubscriptionHandler(stripe_api_key, service_confirmed_path, subscriptions_path))
    resource.putChild('support', Redirect("https://leastauthority.zendesk.com/home"))

    site = Site(resource, logPath=site_logs_path.path)
    site.displayTracebacks = True
    return site


EXPECTED_DOMAIN = 'leastauthority.com'

class RedirectToHTTPS(Resource):
    """
    I redirect to the same path at https:, rewriting *.EXPECTED_DOMAIN -> EXPECTED_DOMAIN.
    Thanks to rakslice at http://stackoverflow.com/questions/5311229/redirect-http-to-https-in-twisted
    """
    isLeaf = 0

    def __init__(self, port, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.port = port

    def render(self, request):
        newpath = request.URLPath()
        assert newpath.scheme != "https", "https->https redirection loop: %r" % (request,)
        newpath.scheme = "https"
        host = newpath.netloc.split(':')[0]
        if host.endswith('.' + EXPECTED_DOMAIN):
            host = EXPECTED_DOMAIN
        if self.port == 443:
            newpath.netloc = host
        else:
            newpath.netloc = "%s:%d" % (host, self.port)
        return redirectTo(newpath, request)

    def getChild(self, name, request):
        return self


def make_redirector_site(port):
    site = Site(RedirectToHTTPS(port))
    site.displayTracebacks = True
    return site
