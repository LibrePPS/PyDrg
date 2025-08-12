import jpype


class UrlLoader:
    def __init__(self):
        if not jpype.isJVMStarted():
            raise RuntimeError(
                "JVM is not started. Please start the JVM before using UrlLoader."
            )
        # Get the URL class loader from Java to prevent classpath issues with other CMS pricers
        self.url_class_loader = jpype.JClass("java.net.URLClassLoader")
        self.url_class = jpype.JClass("java.net.URL")
        self.url_array_class = jpype.JClass("[Ljava.net.URL;")

    def load_urls(self, urls):
        """
        Load the given URLs into the JVM classpath using URLClassLoader.

        :param urls: List of URLs to load.
        """
        url_objects = self.url_array_class(len(urls))
        for i, url in enumerate(urls):
            url_objects[i] = self.url_class(url)
        self.class_loader = self.url_class_loader(url_objects)
        return
