// this is just a way of having a place to import the "Urls" which is actually injected by django
// into the HTML template, with https://github.com/vintasoftware/django-js-reverse
// we could use the js-library, but that requires making a network-call which is just not necessary

const Urls = window.Urls;

export default Urls;
