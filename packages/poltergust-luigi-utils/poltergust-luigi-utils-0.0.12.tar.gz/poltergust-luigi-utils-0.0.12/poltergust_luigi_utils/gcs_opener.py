import luigi
import luigi.contrib.gcs
import luigi.format
import luigi.contrib.opener
try:
    import luigi.contrib.gcs as gcs
except:
    gcs = None
else:
    client = gcs.GCSClient()

class GCSOpener(luigi.contrib.opener.Opener):
    """Opens a target stored on Google GCS

    examples:
    * gs://bucket/foo/bar.txt

    """
    names = ['gs']
    allowed_kwargs = {
        'format': True,
        'client': True,
    }
    filter_kwargs = False

    @classmethod
    def get_target(cls, scheme, path, fragment, username,
                   password, hostname, port, query, **kwargs):
        query.update(kwargs)
        if "client" not in query:
            query["client"] = client
        return gcs.GCSTarget('{scheme}://{hostname}{path}'.format(
            scheme=scheme, hostname=hostname, path=path), **query)
    
luigi.contrib.opener.opener.add(GCSOpener)
