def __init__(self, chan, id, node: TcfNodeExecContext, session):
        self.__chan = chan
        self._ctx = node.id
        self._name = node.get_run_context_data().getName()
        self._id = id
        self._node = node
        self.session = session

def __getattr__(self, name):

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(Target) if callable(getattr(Target, method)) if
                              not method.startswith('_')]
            for method in public_methods:
                if is_ss(method, name):
                    matches.append(method)
            if len(matches) == 0:
                raise NameError(f"Unknown attribute '{name}'") from None
            if len(matches) > 1:
                raise NameError(f"Ambiguous attribute '{name}': {matches}") from None
            return getattr(self, matches[0])(*args, **kwargs)

        return unknown

def _get_all_children_of_the_node(self, node):
        child_data = exec_as_runnable(get_cache_data, node.get_children())
        children = child_data['children'] if 'children' in child_data else None
        if children is not None:
            for child, child_node in children.copy().items():
                children.update(self._get_all_children_of_the_node(child_node))
        return children

def loadhw(self, *args, hw=None, mem_ranges=None):
        """
        loadhw:
            Load a Vivado HW design, and set the memory map for the current
            target. If the current target is a parent for a group of
            processors, memory map is set for all its child processors.
            If current target is a processor, memory map is set for all the
            child processors of it's parent. This command returns the HW
            design object.

        Prototype:
            :class:`target.loadhw(args, hw, mem_ranges)`

        Optional Arguments:
            mem_ranges
                List of memory ranges from which the memory map should be set.
                Memory map is not set for the addresses outside these ranges.
                If this option is not specified, then memory map is set for all
                the addresses in the hardware design.

        Options:
            -regs
                Add registers to memory map.

            -list
                Return a list of open designs for the targets.

        Returns:
            Design object
                If the HW design is loaded and memory map is set successfully.
            Exception:
                Failed to open hw design.

        Examples:
            target.loadhw(hw=design.xsa)
                Load the HW design named design.hdf and set memory map for all
                the child processors for which xc7z045 is the parent.
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='loadhw options')
        parser.add_argument('-l', '--list', action='store_true', help='List open hw designs')
        parser.add_argument('-r', '--regs', action='store_true', help='Add registers to memory map')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        regs = 1 if parsed_args.regs is True else 0
        list_arg = 1 if parsed_args.list is True else 0
        if list_arg:
            if parsed_args.regs or hw is not None or mem_ranges is not None:
                raise Exception(f"--list cannot be used with other args") from None
            if len(self.session._designtable) == 0:
                raise Exception(f"No HW designs currently open") from None
            res = '{0:20s} {1:40s}'.format("Targets", "DesignFile")
            res = res + '\n{0:20s} {1:40s}'.format("=======", "==========")
            designtable = self.session._designtable
            ctx_tgt_map = self.session._get_context_target_map()
            for hw, hw_data in designtable.copy().items():
                ids = list()
                design = hw_data['design']
                for target in hw_data['targets']:
                    for ctx, target_id in ctx_tgt_map.items():
                        if ctx == target:
                            ids.append(str(target_id))
                            break
                res = res + '\n{0:20s} {1:40s}'.format(", ".join(ids), hw[0:59])
                pos = 60
                while len(hw) - pos > 0:
                    res = res + '\n{0:20s} {1:61s}'.format('', hw[pos:pos + 60])
                    pos = pos + 61
            print(res)
            return
        else:
            if hw is None:
                raise Exception(f"HW design is needed to set memory map") from None
            hw = os.path.realpath(hw)
            if not os.path.exists(hw):
                raise Exception(f"{hw} file doesnot exist in the path")
            if hw not in self.session._designtable or 'design' not in self.session._designtable[hw]:
                design = HwManager.open_hw_design(hw)
                self.session._designtable[hw] = dict()
                self.session._designtable[hw]['design'] = design
            else:
                design = self.session._designtable[hw]['design']
                HwManager.current_hw_design(design)

            if mem_ranges is not None:
                if len(mem_ranges) == 2 and isinstance(mem_ranges[0], int) and isinstance(mem_ranges[1], int):
                    mem_ranges = [mem_ranges]
                for range in mem_ranges:
                    check_int(range[0])
                    check_int(range[1])
                self.session._designtable[hw]['ranges'] = mem_ranges
            rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()
            while 'ParentID' in rc and rc['ParentID'] != '':
                parent_node = node.info.get_node(rc['ParentID'])
                rc = exec_as_runnable(get_cache_data, parent_node.get_run_context()).getProperties()

            chan = self.session._curchan
            channels = list()
            if 'channels' in self.session._designtable[hw]:
                channels = self.session._designtable[hw]['channels']
                if chan not in channels:
                    channels.append(chan)
            else:
                channels.append(chan)
            self.session._designtable[hw]['channels'] = channels

            ctx = self.session._curtarget._ctx
            tgts = list()
            if 'targets' in self.session._designtable[hw]:
                tgts = self.session._designtable[hw]['targets']
                if ctx not in tgts:
                    tgts.append(ctx)
            else:
                tgts.append(ctx)
            self.session._designtable[hw]['targets'] = tgts

            self.__set_memmap(chan, ctx, hw, regs)
            return design

def unloadhw(self):
        """
        unloadhw:
            Close the Vivado hardware design which was opened during the loadhw
            command, and clear the memory map for the current target.
            If the current target is a parent for a group of processors, the memory
            map is cleared for all its child processors. If the current target is a
            processor, the memory map is cleared for all the child processors of its
            parent. This command does not clear the memory map explicitly set by
            users through the memmap command.

        Prototype:
            :class:`target.unloadhw()`

        Returns:
            Nothing.

        Examples:
            target.unloadhw()
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None
        designtable = self.session._designtable
        memmap_ctxs = self.session._memmap_ctxs
        chan = self.session._curchan
        ctx = self.session._curtarget._ctx
        rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()
        while 'ParentID' in rc and rc['ParentID'] != '':
            ctx = rc.get('ParentID')
            n = node.info.get_node(rc.get('ParentID'))
            rc = exec_as_runnable(self.__get_run_ctx, n).getProperties()

        if not chan in memmap_ctxs:
            return
        for hw, hw_data in designtable.copy().items():
            if 'targets' in hw_data:
                targets = hw_data['targets']
                if ctx in targets:
                    self.__clear_memmap(node, chan, ctx)
                    targets.remove(ctx)
                    if len(targets) == 0:
                        hw_data['design'].close()
                        designtable.pop(hw)
                    else:
                        designtable[hw]['targets'] = targets
                    break