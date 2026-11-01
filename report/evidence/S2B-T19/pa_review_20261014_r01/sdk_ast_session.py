def __get_debug_targets_properties(self, tgts, jtag_tgts):
        tgts_properties_dict = {}
        port_descriptions = dict()
        self.__get_device_indices(jtag_tgts)
        jtag_ctx_node_map = self._model.launch_node.get_jtag_context_node_map()
        for ctx, tgt in tgts.items():
            if ctx == '':
                continue
            data = {'target_id': tgt['target_id'], 'target_ctx': tgt['id'], 'level': tgt['level'], 'name': '',
                    'parent_ctx': '', 'parent': '', 'state_reason': '', 'is_current': None, 'bscan': '',
                    'jtag_device_id': None, 'jtag_device_ctx': '', 'jtag_device_index': None, 'jtag_device_name': '',
                    'jtag_cable_id': None, 'jtag_cable_ctx': '', 'jtag_cable_name': '', 'jtag_cable_manufacturer': '',
                    'jtag_cable_product': '', 'jtag_cable_serial': ''}
            rc = tgt.get('run_context', None)
            if rc is not None:
                if 'Name' in rc.keys():
                    data['name'] = rc['Name']
                else:
                    data['name'] = tgt['id']
                if 'AdditionalInfo' in rc.keys():
                    data['name'] += rc['AdditionalInfo']
                data['parent_ctx'] = ""
                data['parent'] = ""
                if tgt['parent'] != "":
                    data['parent'] = tgt['parent']
                    data['parent_ctx'] = rc['ParentID']
                rs = tgt['run_state']
                reason = ''
                if rs is not None:
                    if rs.is_suspended is False:
                        if 'StateName' in rs.state_data:
                            reason = rs.state_data['StateName']
                        else:
                            reason = 'Running'
                    elif rs.is_suspended is True:
                        reason = rs.suspend_reason
                    else:
                        reason = "Stopped"
                data['state_reason'] = reason
                data['is_current'] = 0
                if self._curtarget is not None and self._curtarget._id == tgt['target_id']:
                    data['is_current'] = 1
                data['bscan'] = rc['JtagChain'] if 'JtagChain' in rc else ''
                jtaggroup = rc['JtagGroup'] if 'JtagGroup' in rc else None
                if jtaggroup is None:
                    tgts_properties_dict.update({ctx: data})
                    continue
                jtagrc = tgts[jtaggroup]['run_context']
                if jtagrc is not None and 'JtagNodeID' in jtagrc:
                    jtag_node_id = jtagrc['JtagNodeID']
                    node = jtag_tgts[jtag_node_id]
                    node_props = node['props']
                    data['jtag_device_id'] = node_props['node_id']
                    data['jtag_device_ctx'] = node_props['target_ctx']
                    data['jtag_device_index'] = node_props['index'] if 'index' in node_props else 0
                    if 'name' in node_props:
                        data['jtag_device_name'] = node_props['name']
                    while node['parent'] != "":
                        node = jtag_tgts[node['parent']]
                    data['jtag_cable_id'] = node['props']['node_id']
                    data['jtag_cable_ctx'] = node['props']['target_ctx']
                    data['jtag_cable_name'] = node['props']['jtag_cable_name']
                    jtag_node = jtag_ctx_node_map[data['jtag_cable_ctx']]
                    jtag_cable_node = jtag_node.get_jtag_cable_node()

                    if jtag_cable_node is not None:
                        exec_as_runnable(get_cache_data, jtag_cable_node.get_jtag_cable_open_servers())
                        if len(jtag_cable_node.jtag_cable_port_descriptions):
                            for server, server_node in jtag_cable_node.jtag_cable_port_descriptions.items():
                                port_descriptions.update({server: exec_as_runnable(get_cache_data, server_node)})
                    for server, port_desc in port_descriptions.items():
                        if len(port_desc):
                            port_desc = port_desc[0]
                            if port_desc['NodeID'] == data['jtag_cable_ctx']:
                                data['jtag_cable_manufacturer'] = port_desc['Manufacturer']
                                data['jtag_cable_product'] = port_desc['ProductID']
                                data['jtag_cable_serial'] = port_desc['Serial']
                                name = ''
                                if (('Description' in port_desc and port_desc['Description'] != "") and
                                        not ('isError' in port_desc and port_desc['isError']) and
                                        not ('isInitializing' in port_desc and port_desc['isInitializing'])):
                                    name = port_desc['Description']
                                    if 'Serial' in port_desc and port_desc['Serial'] != "":
                                        name = name + ' ' + port_desc['Serial']
                                else:
                                    if 'Manufacturer' in port_desc and port_desc['Manufacturer'] != "":
                                        name = port_desc['Manufacturer']
                                        if 'ProductID' in port_desc and port_desc['ProductID'] != "":
                                            name = name + ' ' + port_desc['ProductID']
                                        else:
                                            name = name + ' cable'
                                        if 'Serial' in port_desc and port_desc['Serial'] != "":
                                            name = name + ' ' + port_desc['Serial']
                                    elif 'ProductID' in port_desc and port_desc['ProductID'] != "":
                                        name = port_desc['ProductID']

                                data['jtag_cable_name'] = name
                                break
            tgts_properties_dict.update({ctx: data})
        return tgts_properties_dict

def targets(self, *args, **kwargs):
        """
        targets:
            List all targets or switch between targets.

        Prototype:
            :class:`tlist = session.targets(kwargs)
            List all the targets.`
            :class:`session.targets(id = <target_id>, kwargs)
            Select <target id> as active target.`

        Arguments:
            kwargs
                id = <target_id>
                    Target to be selected as active target.

                index = <index>
                    Include targets based on jtag scan chain position.
                    This is identical to specifying -filter
                    "jtag_device_index==<index>".

                timeout = <sec>
                    Poll until the targets specified by filter option are found
                    on the scan chain, or until timeout. This option is valid
                    only with filter option. The timeout value is in seconds.
                    Default timeout is 3 seconds.

                filter = <filter-expression>
                    Specify filter expression to control which targets are
                    included in list based on its properties. Filter
                    expressions support operators ==, !=, =~, !~, and, or
                    Strings must be quoted. String matching operators =~ and
                    !~ match lhs string with rhs pattern using or string match.

        Options:
            --set (-s)
                Set current target to entry single entry in list. This is
                useful in comibination with -filter option.  An error will
                be generate if list is empty or contains more than one entry.
            --nocase (-n)
                Use case insensitive filter matching
            --target-properties (-t)
                Returns a list of dictionaries containing target properties.

        Returns:
            Target list when target id is not mentioned.
            None when target id is mentioned.

        Examples:
            session.ta() | session.targets()
                List all the targets.
            session.targets(id = 2)
                Set target with id 2 as active target.
            session.ta('-s', filter='name=~*A9*0')
                Set target whose name matches wildcard "*A9*0" as active target.
            session.targets("--set", filter='(name =~ MicroBlaze #0*) and (bscan==USER2)')
                Set target whose name matches wildcard "MicroBlaze #0*" and bscan is USER2.

        Interactive mode examples:
            targets -id 2
            targets -set -filter '(name=~*A9*0)'
            ta -set -filter '(name=~*A9*0) and (parent == APU)'
            ta -target_properties -id 2
        """

        parser = argparse.ArgumentParser(description='targets')
        parser.add_argument('-s', '--set', action='store_true', help='O')
        parser.add_argument('-l', '--list', action='store_true', help='O')
        parser.add_argument('-t', '--target_properties', action='store_true', help='O')
        parser.add_argument('id', nargs='?', help='Target id')
        parser.add_argument('-n', '--nocase', action='store_true', help='Case insensitive match in filter')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))
        id = check_int(kwargs.pop("id")) if 'id' in kwargs else None
        filter = kwargs.pop("filter", None)
        timeout = 3000 if 'timeout' not in kwargs else check_int(kwargs.pop('timeout'))
        case_insensitive_match = 1 if parsed_args.nocase is True else 0
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        if parsed_args.id is not None:
            if id is not None:
                raise Exception("Conflicting args: Specify target id either as positional arg or keyword arg")
            id = int(parsed_args.id)

        if self._curchan is None:
            raise Exception("Invalid target. Use 'connect' command to connect to hw_server/TCF agent")

        tgts = exec_as_runnable(self._get_targets)
        jtag_tgts = {}
        if jtag_service.NAME in sorted(protocol.invokeAndWait(self.session._curchan_obj.getRemoteServices)):
            jtag_tgts = exec_as_runnable(self._model.launch_node.jtag_targets)
        target_ctx_map = self._model.launch_node.get_target_context_map()
        debug_target_properties = self.__get_debug_targets_properties(tgts, jtag_tgts)
        if parsed_args.target_properties:
            tp = {}
            if id is None:
                return debug_target_properties
            else:
                tp.update({target_ctx_map[id]: debug_target_properties[target_ctx_map[id]]})
            return tp

        if id is not None:
            if id not in target_ctx_map.keys():
                raise Exception(f"No target with id {id}") from None
            node = self._model.get_node(target_ctx_map[id])
            ctx = node.get_run_context_data().getID()

            for t in self._targets:
                if ctx == t.ctx:
                    self._curtarget = t
                    self._current_node = node
                    t._node = node
                    return t
            t = xsdb.target.Target(self._curchan, id, node, xsdb.debug_session)
            self._targets.append(t)
            self._curtarget = t
            self._current_node = node
            return t

        # Filter based on properties
        if filter is not None:
            ctx = None
            new_targets = []
            new_tgts = {}
            # TODO - proper handling
            # temp hack to add () if () are not present at the front and end of the filter string
            if filter[0] != '(':
                filter = '(' + filter + ')'
            if filter.count('(') != filter.count(')'):
                raise Exception('Braces missing in the filter option.') from None
            filter_stack_list = self.__filter_parser(filter)
            filter_stack = []
            for stk in filter_stack_list:
                if isinstance(stk, list):
                    filter_stack = stk
            start_time = round(time.time() * 1000)
            delta = 0
            while delta < timeout:
                for ctx_id, tgt in tgts.items():
                    if ctx_id == '':
                        continue
                    props = debug_target_properties[ctx_id]
                    if self.__parse_filter_string(filter_stack, props, 0, case_insensitive_match):
                        id = tgt['target_id']
                        ctx = tgt['id']
                        name = tgt['run_context']['Name']
                        new_targets.append(name)
                        new_tgts.update({ctx: tgt})
                if len(new_targets):
                    break
                tgts = exec_as_runnable(self._get_targets)
                target_ctx_map = self._model.launch_node.get_target_context_map()
                delta = round(time.time() * 1000) - start_time

            if parsed_args.set:
                if id is None or ctx is None:
                    raise Exception(f"No target with filter '{filter}'") from None
                if len(new_targets) > 1:
                    raise Exception(f"More than one targets with filter '{filter}':", new_targets) from None
                node = self._model.get_node(target_ctx_map[id])
                for t in self._targets:
                    if ctx == t.ctx:
                        self._curtarget = t
                        self._current_node = node
                        return t

                t = xsdb.target.Target(self._curchan, id, node, xsdb.debug_session)
                self._targets.append(t)
                self._curtarget = t
                self._current_node = node
                return t
            else:
                tgts = new_tgts

        result = self.__print_targets(tgts)
        if parsed_args.list == 0:
            print(result)
        else:
            return result.split('\n')