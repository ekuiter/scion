# Copyright 2014 ETH Zurich

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
:mod:`trc` --- SCION TRC parser
===========================================
"""

from lib.crypto.nacl import crypto_sign_ed25519_open
import time
import json
import logging
import os
import base64


class TRC(object):
    """
    The TRC class parses the TRC file of an ISD and stores such
    information for further use.

    :ivar isd_id: the ISD identifier.
    :type isd_id: int
    :ivar version: the TRC file version.
    :type version: int
    :ivar time: the TRC file creation timestamp.
    :type time: int
    :ivar core_quorum: number of trust roots necessary to sign a new TRC.
    :type core_quorum: int
    :ivar trc_quorum: number of trust roots necessary to sign a new ISD
                      cross-signing certificate.
    :type trc_quorum: int
    :ivar core_isps: the set of core ISPs and their certificates.
    :type core_isps: dict
    :ivar root_cas: the set of root CAs and their certificates.
    :type root_cas: dict
    :ivar core_ads: the set of core ADs and their certificates.
    :type core_ads: dict
    :ivar policies: additional management policies for the ISD.
    :type policies: dict
    :ivar registry_server_addr: the root registry server's address.
    :type registry_server_addr: str
    :ivar registry_server_cert: the root registry server's certificate.
    :type registry_server_cert:str
    :ivar root_dns_server_addr: the root DNS server's address.
    :type root_dns_server_addr: str
    :ivar root_dns_server_cert: the root DNS server's certificate.
    :type root_dns_server_cert: str
    :ivar trc_server_addr: the TRC server's address.
    :type trc_server_addr: str
    :ivar signatures: signatures generated by a quorum of trust roots.
    :type signatures: dict
    """

    def __init__(self, trc_file=None):
        """
        Initialize an instance of the class TRC.

        :param trc_file: the name of the TRC file.
        :type trc_file: str
        :returns: the newly created TRC instance.
        :rtype: :class:`TRC`
        """
        self.isd_id = 0
        self.version = 0
        self.time = 0
        self.core_quorum = 0
        self.trc_quorum = 0
        self.core_isps = {}
        self.root_cas = {}
        self.core_ads = {}
        self.policies = {}
        self.registry_server_addr = ''
        self.registry_server_cert = ''
        self.root_dns_server_addr = ''
        self.root_dns_server_cert = ''
        self.trc_server_addr = ''
        self.signatures = {}
        if trc_file:
            self.parse(trc_file)

    def get_trc_dict(self, with_signatures=False):
        """
        Return the TRC information.

        :param with_signatures: True or False whether the returned data should
                                contain the signatures section or not.
        :type with_signatures: bool
        :returns: the TRC information.
        :rtype: dict
        """
        trc_dict = {
            'isd_id': self.isd_id,
            'version': self.version,
            'time': self.time,
            'core_quorum': self.core_quorum,
            'trc_quorum': self.trc_quorum,
            'core_isps': self.core_isps,
            'root_cas': self.root_cas,
            'core_ads': self.core_ads,
            'policies': self.policies,
            'registry_server_addr': self.registry_server_addr,
            'registry_server_cert': self.registry_server_cert,
            'root_dns_server_addr': self.root_dns_server_addr,
            'root_dns_server_cert': self.root_dns_server_cert,
            'trc_server_addr': self.trc_server_addr}
        if with_signatures:
            trc_dict['signatures'] = self.signatures
        return trc_dict

    def parse(self, trc_file):
        """
        Parse a TRC file and populate the instance's attributes.

        :param trc_file: the name of the TRC file.
        :type trc_file: str
        """
        try:
            with open(trc_file) as trc_fh:
                trc = json.load(trc_fh)
        except (ValueError, KeyError, TypeError):
            logging.error("TRC: JSON format error.")
            return
        self.isd_id = trc['isd_id']
        self.version = trc['version']
        self.time = trc['time']
        self.core_quorum = trc['core_quorum']
        self.trc_quorum = trc['trc_quorum']
        self.core_isps = trc['core_isps']
        self.root_cas = trc['root_cas']
        self.core_ads = trc['core_ads']
        self.policies = trc['policies']
        self.registry_server_addr = trc['registry_server_addr']
        self.registry_server_cert = trc['registry_server_cert']
        self.root_dns_server_addr = trc['root_dns_server_addr']
        self.root_dns_server_cert = trc['root_dns_server_cert']
        self.trc_server_addr = trc['trc_server_addr']
        self.signatures = trc['signatures']

    @classmethod
    def from_values(cls, isd_id, version, core_quorum, trc_quorum, core_isps,
        root_cas, core_ads, policies, registry_server_addr,
        registry_server_cert, root_dns_server_addr, root_dns_server_cert,
        trc_server_addr, signatures):
        """
        Generate a TRC instance.

        :param isd_id: the ISD identifier.
        :type isd_id: int
        :param version: the TRC file version.
        :type version: int
        :param core_quorum: number of trust roots necessary to sign a new TRC.
        :type core_quorum: int
        :param trc_quorum: number of trust roots necessary to sign a new ISD
                           cross-signing certificate.
        :type trc_quorum: int
        :param core_isps: the set of core ISPs and their certificates.
        :type core_isps: dict
        :param root_cas: the set of root CAs and their certificates.
        :type root_cas: dict
        :param core_ads: the set of core ADs and their certificates.
        :type core_ads: dict
        :param policies: additional management policies for the ISD.
        :type policies: dict
        :param registry_server_addr: the root registry server's address.
        :type registry_server_addr: str
        :param registry_server_cert: the root registry server's certificate.
        :type registry_server_cert:str
        :param root_dns_server_addr: the root DNS server's address.
        :type root_dns_server_addr: str
        :param root_dns_server_cert: the root DNS server's certificate.
        :type root_dns_server_cert: str
        :param trc_server_addr: the TRC server's address.
        :type trc_server_addr: str
        :param signatures: signatures generated by a quorum of trust roots.
        :type signatures: dict
        :returns: the newly created TRC instance.
        :rtype: :class:`TRC`
        """
        trc = TRC()
        trc.isd_id = isd_id
        trc.version = version
        trc.time = int(time.time())
        trc.core_quorum = core_quorum
        trc.trc_quorum = trc_quorum
        trc.core_isps = core_isps
        trc.root_cas = root_cas
        trc.core_ads = core_ads
        trc.policies = policies
        trc.registry_server_addr = registry_server_addr
        trc.registry_server_cert = registry_server_cert
        trc.root_dns_server_addr = root_dns_server_addr
        trc.root_dns_server_cert = root_dns_server_cert
        trc.trc_server_addr = trc_server_addr
        trc.signatures = signatures
        return trc

    def get_public_key(self, subject):
        """
        Extract the public key of a particular subject.

        :param subject: public key's subject.
        :type subject: str
        :returns: the public key.
        :rtype: str
        """
        if subject not in self.core_ads:
            logging.warning("The public key could not be found.")
            return ''
        subject_cert = self.core_ads[subject].encode('ascii')
        subject_cert = base64.standard_b64decode(subject_cert).decode('ascii')
        subject_cert = json.loads(subject_cert)
        public_key = subject_cert['subject_pub_key'].encode('ascii')
        public_key = base64.standard_b64decode(public_key)
        return public_key

    def verify(self):
        """
        Perform signatures verification.

        :returns: True or False whether the verification succeeds or fails.
        :rtype: bool
        """
        data_to_verify = self.get_trc_dict()
        data_to_verify = json.dumps(data_to_verify, sort_keys=True, indent=4)
        data_to_verify = data_to_verify.encode('ascii')
        for signer in self.signatures:
            if signer not in self.core_ads:
                logging.warning("A signature could not be verified.")
                return False
            public_key = self.get_public_key(signer)
            sig_to_verify = self.signatures[signer].encode('ascii')
            sig_to_verify = base64.standard_b64decode(sig_to_verify)
            signature = sig_to_verify + data_to_verify
            try:
                crypto_sign_ed25519_open(signature, public_key)
            except:
                logging.warning("A signature is not valid.")
                return False
        return True

    def __str__(self):
        """
        Convert the instance in a readable format.

        :returns: the TRC information.
        :rtype: str
        """
        trc_dict = self.get_trc_dict(True)
        trc_str = json.dumps(trc_dict, sort_keys=True, indent=4)
        return trc_str
