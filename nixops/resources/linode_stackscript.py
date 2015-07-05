import nixops.resources, nixops.util, linode.api, nixops.linode_utils

class LinodeStackScriptDefinition(nixops.resources.ResourceDefinition):
    """Definition of a Linode stack script."""
    
    def __init__(self, xml):
        nixops.resources.ResourceDefinition.__init__(self, xml)        
        self.api_keyfile = xml.find("attrs/attr[@name='apiKeyfile']/string").get("value")
        self.label = xml.find("attrs/attr[@name='label']/string").get("value")
        self.description = xml.find("attrs/attr[@name='description']/string").get("value")
        self.distribution_id_list = \
          [ int(elt.get("value")) for elt in xml.findall("attrs/attr[@name='distributionIDList']/list/int") ]
        self.is_public = xml.find("attrs/attr[@name='isPublic']/bool").get("value")
        self.rev_note = xml.find("attrs/attr[@name='revNote']/string").get("value")
        self.script = xml.find("attrs/attr[@name='script']/string").get("value")

    @classmethod
    def get_type(cls):
        return "linode-stackscript"

class LinodeStackScriptState(nixops.resources.ResourceState):
    """State of a Linode stack script."""

    state = nixops.util.attr_property("state", nixops.resources.ResourceState.MISSING, int)
    stack_script_id = nixops.util.attr_property("stack_script_id", None, int)
    api_keyfile = nixops.util.attr_property("api_keyfile", None)
    label = nixops.util.attr_property("label", None)
    description = nixops.util.attr_property("description", None)
    distribution_id_list = nixops.util.attr_property("distribution_id_list", None)
    is_public = nixops.util.attr_property("is_public", None, bool)
    rev_note = nixops.util.attr_property("rev_note", None)
    script = nixops.util.attr_property("script", None)

    @classmethod
    def get_type(cls):
        return "linode-stackscript"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._api = None

    @property
    def resource_id(self):
        return self.name

    def get_definition_prefix(self):
        return "resources.linodeStackScripts."

    def connect(self):
        conn = nixops.linode_utils.get_connection_by_keyfile(self.api_keyfile)
        if conn is None:
            raise Exception("Please give an apiKeyfile or set $LINODE_API_KEY")
        else:
            return conn        
    
    def create(self, defn, check, allow_reboot, allow_recreate):
        self.api_keyfile = defn.api_keyfile
        conn = self.connect()

        if check and self.stack_script_id:
            realstate = conn.stackscript.list(stackscriptid=self.stack_script_id)
            assert len(realstate) <= 1
            if realstate == []:
                self.state = self.MISSING
            else:
                realstate = realstate[0]
                with self.depl._db:
                    self.state = self.UP
                    assert realstate[u'STACKSCRIPTID'] == self.stack_script_id
                    self.label = str(realstate[u'LABEL'])
                    self.description = str(realstate[u'DESCRIPTION'])
                    self.distribution_id_list = \
                      [ int(distid) for distid in realstate[u'DISTRIBUTIONIDLIST'].split(',') ]
                    self.is_public = bool(realstate[u'ISPUBLIC'])
                    self.rev_note = str(realstate[u'REV_NOTE'])
                    self.script = str(realstate[u'SCRIPT'])

        legal_distids = frozenset([ int(dist[u'DISTRIBUTIONID']) \
                                    for dist in nixops.linode_utils.get_distributions(conn) ])
        filtered_distids = list()
        for distid in defn.distribution_id_list:
            if distid in legal_distids:
                filtered_distids.append(distid)
            else:
                self.logger.warn('Skipping unrecognized distribution ID %d' % (distid,))
        filtered_distid_string = ','.join([str(x) for x in filtered_distids])

        if self.state == self.MISSING:
            result = conn.stackscript.create(
                label=defn.label,
                distributionidlist=filtered_distid_string,
                script=defn.script,
                description=defn.description,
                ispublic=defn.is_public,
                rev_note=defn.rev_note)
            with self.depl._db:
                self.state = self.UP
                self.stack_script_id = result[u'StackScriptID']
                self.label = defn.label
                self.description = defn.description
                self.distribution_id_list = filtered_distid_string
                self.is_public = defn.is_public
                self.rev_note = defn.rev_note
                self.script = defn.script
        elif (defn.label != self.label or \
                defn.description != self.description or \
                filtered_distids != self.distribution_id_list or \
                defn.is_public != self.is_public or \
                defn.script != self.script):
            def if_changed(x,y):
                if x == y: return None
                else: return x
            conn.stackscript.update(
                self.stack_script_id,
                label=if_changed(defn.label,self.label),
                description=if_changed(defn.description,self.description),
                distributionidlist=if_changed(filtered_distid_string,self.distribution_id_list),
                ispublic=if_changed(defn.is_public,self.is_public),
                rev_note=defn.rev_note,
                script=if_changed(defn.script,self.script))
            with self.depl._db:
                self.label = defn.label
                self.description = defn.description
                self.distribution_id_list = filtered_distid_string
                self.is_public = defn.is_public
                self.rev_note = defn.rev_note
                self.script = defn.script        

    def destroy(self, wipe=False):
        if self.stack_script_id:
            conn = self.connect()
            conn.stackscript.delete(self.stack_script_id)
        return True
