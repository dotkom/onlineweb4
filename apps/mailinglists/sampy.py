#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as etree
from urllib.request import urlopen, Request
from urllib.error import HTTPError

NAMESPACE_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"
NAMESPACE_SYMPA = "urn:sympasoap"
NAMESPACE_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NAMESPACE_SOAPENC = "http://schemas.xmlsoap.org/soap/encoding/"
NAMESPACE_XSD = "http://www.w3.org/2001/XMLSchema"
NAMESPACE_WSDL = "https://sympa.uio.no/bio.uio.no/wsdl"

NSMAP = {"soap": NAMESPACE_SOAP,
         "sympa": NAMESPACE_SYMPA,
         "xsi": NAMESPACE_XSI,
         "soapenc": NAMESPACE_SOAPENC,
         "xsd": NAMESPACE_XSD,
         "wsdl": NAMESPACE_WSDL}


def soap_wrap(messagetype, elements, parameters=None):
    envelope_attributes = {"soap:encodingStyle": NAMESPACE_SOAPENC,
                           "xmlns:soap": NAMESPACE_SOAP,
                           "xmlns:sympa": NAMESPACE_SYMPA,
                           "xmlns:xsi": NAMESPACE_XSI,
                           "xmlns:xsd": NAMESPACE_XSD,
                           "xmlns:soapenc": NAMESPACE_SOAPENC,
                           "xmlns:wsdl": NAMESPACE_WSDL}
    envelope = etree.Element("soap:Envelope", attrib=envelope_attributes)
    body = etree.SubElement(envelope, "soap:Body")
    nodetype = etree.SubElement(body, "sympa:" + messagetype)

    for key, value in elements:
        etree.SubElement(nodetype, key).text = value

    if parameters:
        attribs = {"xsi:type": "wsdl:ArrayOfString",
                   "soapenc:arrayType": "xsd:string[%i]" % len(parameters)}
        param = etree.SubElement(nodetype, "parameters", attrib=attribs)
        for p in parameters:
            etree.SubElement(
                param,
                "item",
                attrib={"xsi:type": "xsd:string"}).text = p

    return etree.tostring(envelope, encoding="UTF-8")


class Sampy(object):

    def __init__(self, url, appname=None, password=None, admin_account=None):
        self.url = url
        self.appname = appname
        self.password = password
        self.admin_account = admin_account
        self.cookie = None
        self.email = None

    def login(self, email, password):
        xml = soap_wrap("login", (("email", email), ("password", password)))
        request = Request(self.url)
        request.add_header("Content-Type", "text/xml")
        request.add_data(xml)
        response = urlopen(request)
        response_tree = etree.parse(response).getroot()
        self.cookie = response_tree[0][0][0].text
        self.email = email

    def lists(self, topic=None, subtopic=None):
        if not self.appname:
            returnlists = self.authenticate_and_run(self.email, "lists")
        else:
            returnlists = self.authenticate_remote_app_and_run("USER_EMAIL=" + self.admin_account, "lists")

        ret = []
        for l in returnlists:
            element = {}
            variables = l.split(";")
            for v in variables:
                key, value = v.split("=")
                element[key] = value
            ret.append(element)
        return ret

    def review(self, listname):
        if not self.appname:
            review = self.authenticate_and_run(self.email, "review", [listname])
        else:
            review = self.authenticate_remote_app_and_run("USER_EMAIL=" + self.admin_account, "review", [listname])
        return [r for r in review]

    def which(self):
        if not self.appname:
            which = self.authenticate_and_run(self.email, "which")
        else:
            which = self.authenticate_remote_app_and_run("USER_EMAIL=" + self.admin_account, "which")
        return which

    def authenticate_and_run(self, email, service, parameters=None):
        arguments = (("email", email),
                     ("cookie", self.cookie),
                     ("service", service))
        xml = soap_wrap("authenticateAndRun", arguments, parameters)
        request = Request(self.url)
        request.add_header("Content-Type", "text/xml")
        request.add_data(xml)
        try:
            response = urlopen(request)
        except HTTPError as e:
            print(e.read())
            return
        responsetree = etree.fromstring(response.read())
        return [r.text for r in responsetree[0][0][0]]

    def authenticate_remote_app_and_run(self, variables, service, parameters=None):
        arguments = (("appname", self.appname),
                     ("apppassword", self.password),
                     ("vars", variables),
                     ("service", service))
        xml = soap_wrap("authenticateRemoteAppAndRun", arguments, parameters)
        request = Request(self.url)
        request.add_header("Content-Type", "text/xml")
        request.add_data(xml)
        try:
            response = urlopen(request)
        except HTTPError as e:
            print(e.read())
            return
        responsetree = etree.fromstring(response.read())

        # TODO: Dette er den styggeste hacken in the history of mankind. Finn ut av encoding her.
        return [r.text.encode("iso-8859-1").replace("Ã¥", "å") for r in responsetree[0][0][0]]
