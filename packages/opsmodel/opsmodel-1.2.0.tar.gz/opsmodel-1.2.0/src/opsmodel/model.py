
############################################################################
# Created by :  Okhtai alizadeh arasi
# LinkedIn URL: linkedin.com/in/oktai-alizade-94aa5538
# Mobile - whatsapp: +989144011724
# Telegram channel: https://t.me/OKprograms
# Instagram: opensees_apps
############################################################################

import numpy as np
import copy
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches
import matplotlib
import os
import shutil
import pandas as pd
import numbers
from datetime import datetime
import matplotlib.cm as cm
from matplotlib import pyplot as plt
import dill
import pyarrow

def create_model(ops, name='mymodel', ndm=3, ndf=6, tolerance=1e-10, wipe=True):
    global _name
    global _ndm
    global _ndf
    global _tolerance
    global masssource

    if not isinstance(name, str):
        raise TypeError('Model Name must be string !')
    if len(name.strip()) == 0:
        raise TypeError('Model Name must be string !')

    _name = name
    masssource = []

    if wipe:
        ops.wipe()
    ops.model('basic', '-ndm', ndm, '-ndf', ndf)

    _ndm = ndm
    _ndf = ndf
    _tolerance = tolerance

    mymodel = Model(ops, name, ndm, ndf, tolerance, wipe)
    return mymodel
class Model:
    def __init__(self, ops, name='mymodel', ndm=3, ndf=6, tolerance=1e-10, wipe=True):
        self.ops = ops
        self.Name = name
        self.Ndm = ndm
        self.Ndf = ndf
        self.Tolerance = tolerance
        self.Parts = []
        self.CreatedParts = []
        self.Wipe = wipe
        self.Masssource = []
        self.QuadUniLoads = []
        self.BodyLoads = []
        self.SurfLoads = []
        self.NodalLoads = []
        self.NodalMasses = []
        self.SpConstraints = []
        self.EqualDofs = []
        self.RigidDiaphragms = []
        self.createdRgDiapgh = []
        self.RigidLinks = []
        self.geomTransf = []
        self.MassCenters = {}
        self.MergedParts = []

    def add_parts(self, *parts):
        if isinstance(parts, Part):
            self.Parts.append(parts)
        elif isinstance(parts, list) or isinstance(parts, tuple):
            for part in parts:
                self.Parts.append(part)
        else:
            raise TypeError('parts must be a Part or list of parts')

    def merge_nodes_parts(self, *parts):
        self.MergedParts.append(list(parts))

    def define_masssource(self, patterns, factors, direction_load=2, direction_mass=[1, 3]):
        if not isinstance(patterns, list):
            patterns = [patterns]
        if not isinstance(factors, list):
            factors = [factors]

        if len(patterns) != len(factors):
            raise ValueError("Number of factors must be the number of load patterns")

        self.Masssource = [patterns, factors, direction_load, direction_mass]

    def assign_nodalload(self, pattern, xyz, value, direction=2, option='add'):
        _tolerance = self.Tolerance
        _ndf = self.Ndf
        dofvals = list(np.arange(1, _ndf + 1, dtype=int))
        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in dofvals:
            raise ValueError('direction must be 1 through ndf')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        uniloads = self.NodalLoads
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                df_xyz = True in (abs((np.array(load[1]) - np.array(xyz))) > _tolerance)
                if df_xyz is False:
                    if (load[0]['Name'] != pattern['Name']):
                        newuniloads.append(load)

            self.NodalLoads = newuniloads
            return

        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                df_xyz = True in (abs((np.array(load[1]) - np.array(xyz))) > _tolerance)
                if df_xyz is False:
                    if load[0]['Name'] != pattern['Name']:
                        newuniloads.append(load)

            newuniloads.append([pattern, xyz, value, direction])
            self.NodalLoads = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            df_xyz = True in (abs((np.array(load[1]) - np.array(xyz))) > _tolerance)
            if df_xyz is False:
                if load[0]['Name'] == pattern['Name'] and load[2] == direction:
                    if option.lower() in ['add', 'a']:
                        uniloads[i][1] += value
                        return

        uniloads.append([pattern, xyz, value, direction])

    def assign_nodalmass(self, xyz, value, direction=2, option='add'):
        _tolerance = self.Tolerance
        _ndf = self.Ndf
        dofvals = list(np.arange(1, _ndf + 1, dtype=int))
        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in dofvals:
            raise ValueError('direction must be 1 through ndf')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        uniloads = self.NodalMasses
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                df_xyz = True in (abs((np.array(load[0]) - np.array(xyz))) > _tolerance)
                if df_xyz is False:
                        newuniloads.append(load)

            self.NodalMasses = newuniloads
            return

        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                df_xyz = True in (abs((np.array(load[0]) - np.array(xyz))) > _tolerance)
                if df_xyz is False:
                        newuniloads.append(load)

            newuniloads.append([xyz, value, direction])
            self.NodalMasses = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            df_xyz = True in (abs((np.array(load[0]) - np.array(xyz))) > _tolerance)
            if df_xyz is False:
                if load[2] == direction:
                    if option.lower() in ['add', 'a']:
                        uniloads[i][1] += value
                        return

        uniloads.append([xyz, value, direction])

    def assign_spconstraint(self, parts=[], xlim=[], ylim=[], zlim=[], dofs=[]):
        _ndf = self.Ndf
        dofs = list(dict.fromkeys(dofs))
        dirvals = list(np.arange(1, _ndf+1, dtype=int))

        if len(dofs) != 0:
            for dir in dofs:
                if dir not in dirvals:
                    raise ValueError('direction must be a integer between 1 through ndf = ' + str(_ndf))

        self.SpConstraints.append([parts, xlim, ylim, zlim, dofs])

    def assign_equaldof(self, xyzr, parts=[], xclim=[], yclim=[], zclim=[], dofs=[]):
        _ndf = self.Ndf
        dofs = list(dict.fromkeys(dofs))
        dirvals = list(np.arange(1, _ndf + 1, dtype=int))
        if len(dofs) != 0:
            for dir in dofs:
                if dir not in dirvals:
                    raise ValueError('dof must be a integer between 1 through ndf = ' + str(_ndf))

        self.EqualDofs.append([parts, xyzr, xclim, yclim, zclim, dofs])

    def assign_rigiddiaphragm(self, xyzr, parts=[], perpdirn=2, xclim=[], yclim=[], zclim=[], massr=[], rests=[2, 4, 6]):
        rgdiaphs = self.RigidDiaphragms
        rgdiaphs.append([parts, xyzr, perpdirn, xclim, yclim, zclim, massr, rests])

    def assign_rigidlink(self, xyzr, parts=[], type='beam', xclim=[], yclim=[], zclim=[]):
        rglinks = self.RigidLinks
        rglinks.append([parts, xyzr, type, xclim, yclim, zclim])

    def getNodes(self, parts=[]):
        model_nodes = {}
        if len(parts) == 0:
            parts = self.CreatedParts

        for part in self.CreatedParts:
            if part in parts:
                for m in part.Components:
                    model_nodes.update(m.Nodes)

        model_nodes.update(self.MassCenters)
        return model_nodes

    def getElements(self):
        model_elements = {}
        for part in self.CreatedParts:
            for m in part.Components:
                model_elements.update(m.Elements)

        return model_elements

    def __linenodalloads(self, xyzi, xyzj, w):
        xi, yi, zi = xyzi
        xj, yj, zj = xyzj
        dx, dy, dz = xj - xi, yj - yi, zj - zi
        l = np.sqrt((dx ** 2 + dy ** 2 + dz ** 2))
        # node i
        return w * l / 2

    def __find_component(self, eletag, part):
        for m in part.Components:
            elements = m.Elements
            for tag in elements.keys():
                if tag == eletag:
                    return m

    def __add_nodeload(self, tag, values, all_nodal_loads):
        values = np.array(values)
        if len(values) < 6:
            n = 6 - len(values)
            values = np.append(values, np.zeros((n, 1)))
        all_nodal_loads.append([tag, values])

    def __add_nodeload_patt(self, patt, tag, values, all_nodal_loads_patt):
        values = np.array(values)
        if len(values) < 6:
            n = 6 - len(values)
            values = np.append(values, np.zeros((n, 1)))

        all_nodal_loads_patt.append([patt, tag, values])

    def __add_lineload_patt(self, patt, tag, values, all_line_loads_patt):
        values = np.array(values)
        if len(values) < 3:
            n = 3- len(values)
            values = np.append(values, np.zeros((n, 1)))

        all_line_loads_patt.append([patt, tag, values])

    def __load_transe_l2g(self, ops, comp, ele, load):
        prop = comp.EleProps
        vecxz = []
        for val in prop.values():
            if isinstance(val, geomTransf):
                vecxz = val.Vecxz
                if len(vecxz) == 0:
                    vecxz = [0, 0, 1]
                break
        if len(vecxz) == 0:
            return load

        ele_nodes = ops.eleNodes(ele)
        xyzi = np.array(ops.nodeCoord(ele_nodes[0]))
        xyzj = np.array(ops.nodeCoord(ele_nodes[1]))
        if len(xyzi) == 2:
            xyzi = np.append(xyzi, 0.0)
            xyzj = np.append(xyzj, 0.0)

        Vx = xyzj - xyzi
        Vy = np.cross(vecxz, Vx)
        Vz = np.cross(Vx, Vy)
        V_G = MyMath.Transform_l2g(load, Vx, Vy, Vz)
        return list(V_G)

    def __load_transe_g2l(self, comp, ele, load):
        ops = self.ops
        prop = comp.EleProps
        vecxz = []
        for val in prop.values():
            if isinstance(val, geomTransf):
                vecxz = val.Vecxz
                if len(vecxz) == 0:
                    vecxz = [0, 0, 1]
                break
        if len(vecxz) == 0:
            return load

        ele_nodes = ops.eleNodes(ele)
        xyzi = np.array(ops.nodeCoord(ele_nodes[0]))
        xyzj = np.array(ops.nodeCoord(ele_nodes[1]))
        if len(xyzi) == 2:
            xyzi = np.append(xyzi, 0.0)
            xyzj = np.append(xyzj, 0.0)
        Vx = xyzj - xyzi
        Vy = np.cross(vecxz, Vx)
        Vz = np.cross(Vx, Vy)
        V_L = MyMath.Transform_g2l(load, Vx, Vy, Vz)
        return list(V_L)

    def __quadnodalloads(self, xyzi, xyzj, xyzk, xyzl, lo):
        w = lo[1]
        dir = int(lo[2])
        coord = lo[3]
        fb = np.zeros((3, 1))
        fb[dir - 1] = w
        return MyFEM.nodalforce_Q4(fb, coord, xyzi, xyzj, xyzk, xyzl)

    def __bricknodalloads(self, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, lo):
        w = lo[1]
        dir = lo[2]
        fb = np.zeros((3, 1))
        fb[dir - 1] = w

        return MyFEM.nodalforce_B8(fb, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8)

    def __quad9nodalloads(self, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, xyz9, lo):
        w = lo[1]
        dir = lo[2]
        coord = lo[3]
        fb = np.zeros((3, 1))
        fb[dir - 1] = w
        return MyFEM.nodalforce_Q9(fb, coord, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, xyz9)

    def __trinodalloads(self, xyzi, xyzj, xyzk, lo):
        w = lo[1]
        dir = lo[2]
        coord = lo[3]
        fb = np.zeros((3, 1))
        fb[dir - 1] = w

        return MyFEM.nodalforce_T3(fb, coord, xyzi, xyzj, xyzk)

    def __applybrickmass(self, component, loadpattern, sfactor, all_nodal_loads):
        ops = self.ops
        if len(component.Surfload) != 0:
            for lo in component.Surfload:
                if lo[0] == loadpattern:
                    face = lo[1]
                    fnodes = component.NodeSets[face]['Nodes']
                    Njk, Nij = len(fnodes), len(fnodes[0])
                    for i in range(Njk - 1):
                        for j in range(Nij - 1):
                            node_s = []
                            node_s.append(fnodes[i][j])
                            node_s.append(fnodes[i][j + 1])
                            node_s.append(fnodes[i + 1][j + 1])
                            node_s.append(fnodes[i + 1][j])
                            xyzi = ops.nodeCoord(node_s[0])
                            xyzj = ops.nodeCoord(node_s[1])
                            xyzk = ops.nodeCoord(node_s[2])
                            xyzl = ops.nodeCoord(node_s[3])
                            lo_ = [lo[0], lo[2], lo[3], lo[4]]
                            W_l, W_g = self.__quadnodalloads(xyzi, xyzj, xyzk, xyzl, lo_)

                            for k in range(4):
                                wx, wy, wz = list(W_g[k])
                                _values = [wx * sfactor, wy * sfactor, wz * sfactor]
                                self.__add_nodeload(node_s[k], _values, all_nodal_loads)

        if len(component.Bodyload) != 0:
            for lo in component.Bodyload:
                if lo[0] == loadpattern:
                    elements = component.Elements
                    for ele in elements.keys():
                        node_s = elements[ele]
                        xyz1 = ops.nodeCoord(node_s[0])
                        xyz2 = ops.nodeCoord(node_s[1])
                        xyz3 = ops.nodeCoord(node_s[2])
                        xyz4 = ops.nodeCoord(node_s[3])
                        xyz5 = ops.nodeCoord(node_s[4])
                        xyz6 = ops.nodeCoord(node_s[5])
                        xyz7 = ops.nodeCoord(node_s[6])
                        xyz8 = ops.nodeCoord(node_s[7])

                        W_g = self.__bricknodalloads(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, lo)

                        for k in range(8):
                            wx, wy, wz = W_g[k]
                            _values = [wx * sfactor, wy * sfactor, wz * sfactor]
                            self.__add_nodeload(node_s[k], _values, all_nodal_loads)

    def __applypointmass(self, component, loadpattern, factor, all_nodal_loads):
        ops = self.ops
        _ndf = self.Ndf
        tag = component.NodeTag
        for lo in component.Pointload:
            pat = lo[0]
            if pat == loadpattern:
                val = lo[1]
                dir = lo[2]
                vals = list(np.zeros(_ndf, dtype=int))
                vals[dir - 1] = val
                _values = [x * factor for x in vals]

                self.__add_nodeload(tag, _values, all_nodal_loads)

    def __assign_line_loads(self, print_command, sfactor, file_loading, all_line_loads_patt):
        if len(all_line_loads_patt) == 0:
            return
        ops = self.ops
        _ndm = self.Ndm
        _ndf = self.Ndf
        _name = self.Name
        line_loads = {}

        for items in all_line_loads_patt:
            val = line_loads.get(items[1])
            if val is None:
                line_loads[items[1]] = np.array(items[2])
            else:
                line_loads[items[1]] = val + np.array(items[2])

        for key, values in line_loads.items():
            str_eletag = str(key)
            wx, wy, wz = list(values)
            if _ndm == 2:
                str_wx, str_wy = str(wx * sfactor), str(wy * sfactor)
                str_command = "ops.eleLoad('-ele', " + str_eletag + ", '-type', '-beamUniform', " + \
                              str_wy + ", " + str_wx + ")"
            else:
                str_wx, str_wy, str_wz = str(wx), str(wy * sfactor), str(wz * sfactor)
                str_command = "ops.eleLoad('-ele', " + str_eletag + ", '-type', '-beamUniform', " + \
                              str_wy + ", " + str_wz + ", " + str_wx + ")"

            if print_command.lower() in ['y', 'yes']:
                print(str_command)

            eval(str_command)
            file_loading.write(str_command + '\n')

        all_nodal_loads_patt = []

    def __assign_nodal_loads(self, print_command, sfactor, file_loading, all_nodal_loads_patt):
        if len(all_nodal_loads_patt) == 0:
            return

        ops = self.ops
        _ndm = self.Ndm
        _ndf = self.Ndf
        _name = self.Name
        nodal_loads = {}

        for items in all_nodal_loads_patt:
            val = nodal_loads.get(items[1])
            if val is None:
                nodal_loads[items[1]] = np.array(items[2])
            else:
                nodal_loads[items[1]] = val + np.array(items[2])

        for key, values in nodal_loads.items():
            str_tag = str(key)
            wx, wy, wz, wxx, wyy, wzz = list(values)
            if all(v == 0 for v in values):
                continue

            if _ndm == 3:
                str_wx, str_wy, str_wz, str_wxx, str_wyy, str_wzz = str(wx * sfactor), str(wy * sfactor), str(wz * sfactor), str(wxx * sfactor), str(wyy * sfactor), str(wzz * sfactor)
                if _ndf == 2:
                    str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ")"
                elif _ndf == 3:
                    str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ")"
                elif _ndf == 6:
                    str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + \
                                  ", " + str_wxx + ", " + str_wyy + ", " + str_wzz + ")"

            else:
                str_wx, str_wy, str_wzz = str(wx * sfactor), str(wy * sfactor), str(wz * sfactor)
                if _ndf == 3:
                    str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wzz + ")"
                elif _ndf == 2:
                    str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ")"

            if print_command.lower() in ['y', 'yes']:
                print(str_command)

            eval(str_command)
            file_loading.write(str_command + '\n')

        all_nodal_loads_patt = []
    def __findmasscenter(self, node_tags_slave, rests, nodal_mass, perpdirn, print_command):
        ops = self.ops
        nodes = self.getNodes()
        _name = self.Name
        _ndf = self.Ndf
        X = []
        Y = []
        Z = []
        M_x = []
        M_y = []
        M_z = []
        for n_s in node_tags_slave:
            X.append(nodes[n_s][0])
            Y.append(nodes[n_s][1])
            Z.append(nodes[n_s][2])
            val = nodal_mass.get(n_s)
            if val is None:
                M_x.append(0.0)
                M_y.append(0.0)
                M_z.append(0.0)
            else:
                M_x.append(nodal_mass[n_s][0])
                M_y.append(nodal_mass[n_s][1])
                M_z.append(nodal_mass[n_s][2])

        X = np.array(X)
        Y = np.array(Y)
        Z = np.array(Z)
        M_x = np.array(M_x)
        M_y = np.array(M_y)
        M_z = np.array(M_z)

        if np.sum(M_x) != 0.0:
            xr = np.sum((X * M_x)) / np.sum(M_x)
        else:
            xr = np.sum(X) / len(X)

        if np.sum(M_y) != 0.0:
            yr = np.sum((Y * M_y)) / np.sum(M_y)
        else:
            yr = np.sum(Y) / len(Y)

        if np.sum(M_z) != 0.0:
            zr = np.sum((Z * M_z)) / np.sum(M_z)
        else:
            zr = np.sum(Z) / len(Z)

        xyzr = [xr, yr, zr]
        # print(xyzr)
        noder = self.__nodeexist_dict(xyzr, nodes)
        file_constraint = open(_name + "\\" + "file_constraint.txt", "a")
        warnnote = ""
        if noder is False:
            warnnote = "# Rigid Diaphragm constraint: Master node was not found. A new node was created as master node"
            print("# Note:")
            print(warnnote)
            rnode = create_node(ops, xyzr, print_command)
            if len(rests) != 0:
                file_fix = open(_name + "\\" + "file_fix.txt", "a")
                restvals = list(np.zeros(_ndf, dtype=int))
                for rs in rests:
                    restvals[rs - 1] = 1

                str_vals = ""
                for rsv in restvals:
                    str_vals = str_vals + ", " + str(rsv)

                str_command = "ops.fix(" + str(rnode) + str_vals + ")"

                file_fix.write(str_command + '\n')

                if print_command.lower() in ['y', 'yes']:
                    print(str_command)
                eval(str_command)
                file_fix.close()

        else:
            rnode = noder

        str_cnodes = ""
        for n in node_tags_slave:
            if n != rnode:
                str_cnodes = str_cnodes + ", " + str(n)

        str_command = "ops.rigidDiaphragm(" + str(perpdirn) + ", " + str(rnode) + str_cnodes + ")"

        file_constraint.write(warnnote + '\n')
        file_constraint.write(str_command + '\n')
        if print_command.lower() in ['y', 'yes']:
            print(str_command)

        eval(str_command)
        file_constraint.close()

        cnodes = self.MassCenters
        cnodes.update({rnode: [xr, yr, zr]})
        self.MassCenters = cnodes

        return rnode


    def __assign_mass(self, g, mass_concentrate, mass_additional,  print_command, all_nodal_loads, n_mass, minval):
        ops = self.ops
        masssource = self.Masssource
        _ndm = self.Ndm
        _name = self.Name
        _ndf = self.Ndf
        load_dir = masssource[2]
        mass_dir = np.array(masssource[3], dtype=int)
        nodal_mass = {}
        rgdiapghs = self.createdRgDiapgh
        for items in all_nodal_loads:
            tag = items[0]
            val = nodal_mass.get(items[0])
            values = items[1]
            mass_val = values[load_dir - 1] / g
            vals = np.zeros(_ndf, dtype=float)
            vals[mass_dir - 1] = abs(mass_val)
            if val is None:
                nodal_mass[tag] = vals
            else:
                nodal_mass[tag] = val + vals

        for tag, mass_val in n_mass.items():
            val = nodal_mass.get(tag)
            mass_val = np.array(mass_val, dtype=float)
            if val is None:
                nodal_mass[tag] = mass_val
            else:
                nodal_mass[tag] = val + mass_val

        for i in range(len(rgdiapghs)):
            if isinstance(rgdiapghs[i][0], str):
                node_tags_slave = rgdiapghs[i][1]
                rests = rgdiapghs[i][3]
                perpdirn = rgdiapghs[i][4]
                rnode = self.__findmasscenter(node_tags_slave, rests, nodal_mass, perpdirn, print_command)
                rgdiapghs[i][0] = rnode

        rigid_dict = {}
        for i in range(len(rgdiapghs)):
            tag = rgdiapghs[i][0]
            node_tags = rgdiapghs[i][1]
            rmass = np.zeros(_ndf)
            if mass_additional.lower() in ['y', 'yes']:
                rmass = rgdiapghs[i][2]
                if len(rmass) == 0:
                    rmass = np.zeros(_ndf)


            val = rigid_dict.get(tag)
            if val is None:
                rigid_dict[tag] = [node_tags, np.array(rmass, dtype=float)]
            else:
                nodes_ = list(rigid_dict[tag][0])
                nodes_.extend(node_tags)
                nodes_ = list(dict.fromkeys(nodes_))
                rmass_ = rigid_dict[tag][1] + np.array(rmass, dtype=float)
                rigid_dict[tag] = [nodes_, rmass_]

        nodal_mass_r = {}
        for rnode, snodes in rigid_dict.items():
            rmass = snodes[1]
            if mass_concentrate.lower() in ['y', 'yes']:
                for snode in snodes[0]:
                    if snode in nodal_mass.keys():
                        rmass += nodal_mass[snode]
                        nodal_mass[snode] = np.zeros(_ndf)
            if rnode in nodal_mass.keys():
                rmass += nodal_mass[rnode]
                nodal_mass[rnode] = np.zeros(_ndf)
            nodal_mass_r[rnode] = rmass

        file_mass = open(_name + "\\" + "file_mass.txt", "w")

        for key, value in nodal_mass.items():
            for i in range(len(value)):
                if value[i] == 0.0:
                    value[i] = minval
            if all(v == minval for v in value):
                continue

            str_vals = ""
            for m in value:
                str_vals = str_vals + ", " + str(m)

            str_command_m = "ops.mass(" + str(key) + str_vals + ")"
            file_mass.write(str_command_m + '\n')
            if print_command.lower() in ['y', 'yes']:
                print(str_command_m)
            eval(str_command_m)

        for key, value in nodal_mass_r.items():
            for i in range(len(value)):
                if value[i] == 0.0:
                    value[i] = minval

            if all(v == minval for v in value):
                continue

            str_vals = ""
            for m in value:
                str_vals = str_vals + ", " + str(m)

            str_command_m = "ops.mass(" + str(key) + str_vals + ")"
            file_mass.write(str_command_m + '\n')
            if print_command.lower() in ['y', 'yes']:
                print(str_command_m)
            eval(str_command_m)

        file_mass.close()

    def apply_mass(self, g, parts=[], mass_concentrate='y', mass_additional='y', minval=1E-10, print_command='n'):
        all_nodal_loads = []
        masssource = self.Masssource
        ops = self.ops
        _ndm = self.Ndm
        if len(parts) == 0:
            parts = self.Parts

        loadpatterns = masssource[0]
        factors = masssource[1]
        n_mass = {}
        if mass_additional.lower() in ['y', 'yes']:
            self.__addmass(None, n_mass)

        for part in parts:
            lineuniloads = part.LineUniLoads
            quaduniloads = part.QuadUniLoads
            nodeloads = part.NodalLoads

            if mass_additional.lower() in ['y', 'yes']:
                self.__addmass(part, n_mass)

            for i in range(len(loadpatterns)):
                loadpattern = loadpatterns[i]
                sfactor = factors[i]
                for el in lineuniloads.keys():
                    if len(lineuniloads[el]) != 0:
                        for lo in lineuniloads[el]:
                            if len(lo) != 0:
                                if lo[0] == loadpattern:
                                    ele_nodes = ops.eleNodes(el)
                                    xyzi = ops.nodeCoord(ele_nodes[0])
                                    xyzj = ops.nodeCoord(ele_nodes[1])
                                    if len(xyzi) == 2:
                                        xyzi.append(0.0)
                                        xyzj.append(0.0)
                                    nodload = self.__linenodalloads(xyzi, xyzj, lo[1])

                                    if _ndm == 2:
                                        wx_m = wy_m = wz_m = 0.0
                                        if lo[2] == 1:
                                            wx_m = nodload
                                        elif lo[2] == 2:
                                            wy_m = nodload
                                        else:
                                            raise ValueError('beam uniform loading: ndm = 2 ==> direction should be 1 or 2')
                                    else:
                                        wx_m = wy_m = wz_m = 0.0
                                        if lo[2] == 1:
                                            wx_m = nodload
                                        elif lo[2] == 2:
                                            wy_m = nodload
                                        elif lo[2] == 3:
                                            wz_m = nodload
                                        else:
                                            raise ValueError(
                                                'beam uniform loading: ndm = 3 ==> direction should be 1, 2 or 3')

                                    if _ndm == 2:
                                        _values = [wx_m * sfactor, wy_m * sfactor, 0.0]
                                    else:
                                        _values = [wx_m * sfactor, wy_m * sfactor, wz_m * sfactor]
                                    comp = self.__find_component(el, part)
                                    if comp != None:

                                        if lo[3].lower() in ['l', 'local']:
                                            _values = self.__load_transe_l2g(ops, comp, el, _values)
                                        self.__add_nodeload(ele_nodes[0], _values, all_nodal_loads)
                                        self.__add_nodeload(ele_nodes[1], _values, all_nodal_loads)
                for el in quaduniloads.keys():
                    if len(quaduniloads[el]) != 0:
                        for lo in quaduniloads[el]:
                            if len(lo) != 0:
                                if lo[0] == loadpattern:
                                    ele_nodes = ops.eleNodes(el)
                                    if len(ele_nodes) == 3:
                                        xyzi = ops.nodeCoord(ele_nodes[0])
                                        xyzj = ops.nodeCoord(ele_nodes[1])
                                        xyzk = ops.nodeCoord(ele_nodes[2])
                                        if len(xyzi) == 2:
                                            xyzi.append(0.0)
                                            xyzj.append(0.0)
                                            xyzk.append(0.0)

                                        W_l, W_g = self.__trinodalloads(xyzi, xyzj, xyzk, lo)
                                        for i in range(3):
                                            wx, wy, wz = list(W_g[i])
                                            if _ndm == 3:
                                                _values = [wx * sfactor, wy * sfactor, wz * sfactor]
                                                self.__add_nodeload(ele_nodes[i], _values, all_nodal_loads)
                                            else:
                                                _values = [wx * sfactor, wy * sfactor, 0]
                                                self.__add_nodeload(ele_nodes[i], _values, all_nodal_loads)

                                    elif len(ele_nodes) == 4:
                                        xyzi = ops.nodeCoord(ele_nodes[0])
                                        xyzj = ops.nodeCoord(ele_nodes[1])
                                        xyzk = ops.nodeCoord(ele_nodes[2])
                                        xyzl = ops.nodeCoord(ele_nodes[3])
                                        if len(xyzi) == 2:
                                            xyzi.append(0.0)
                                            xyzj.append(0.0)
                                            xyzk.append(0.0)
                                            xyzl.append(0.0)
                                        W_l, W_g = self.__quadnodalloads(xyzi, xyzj, xyzk, xyzl, lo)

                                        for i in range(4):
                                            wx, wy, wz = list(W_g[i])
                                            if _ndm == 3:
                                                _values = [wx * sfactor, wy * sfactor, wz * sfactor]
                                                self.__add_nodeload(ele_nodes[i], _values, all_nodal_loads)
                                            else:
                                                _values = [wx * sfactor, wy * sfactor, 0]
                                                self.__add_nodeload(ele_nodes[i], _values, all_nodal_loads)

                                    elif len(ele_nodes) == 9:
                                        xyz1 = ops.nodeCoord(ele_nodes[0])
                                        xyz2 = ops.nodeCoord(ele_nodes[1])
                                        xyz3 = ops.nodeCoord(ele_nodes[2])
                                        xyz4 = ops.nodeCoord(ele_nodes[3])
                                        xyz5 = ops.nodeCoord(ele_nodes[4])
                                        xyz6 = ops.nodeCoord(ele_nodes[5])
                                        xyz7 = ops.nodeCoord(ele_nodes[6])
                                        xyz8 = ops.nodeCoord(ele_nodes[7])
                                        xyz9 = ops.nodeCoord(ele_nodes[8])
                                        if len(xyz1) == 2:
                                            xyz1.append(0.0)
                                            xyz2.append(0.0)
                                            xyz3.append(0.0)
                                            xyz4.append(0.0)
                                            xyz5.append(0.0)
                                            xyz6.append(0.0)
                                            xyz7.append(0.0)
                                            xyz8.append(0.0)
                                            xyz9.append(0.0)
                                        W_l, W_g = self.__quad9nodalloads(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7,
                                                                          xyz8, xyz9, lo)

                                        for i in range(9):
                                            wx, wy, wz = list(W_g[i])
                                            if _ndm == 3:
                                                _values = [wx * sfactor, wy * sfactor, wz * sfactor]
                                                self.__add_nodeload(ele_nodes[i], _values, all_nodal_loads)
                                            else:
                                                _values = [wx * sfactor, wy * sfactor, 0]
                                                self.__add_nodeload(ele_nodes[i], _values, all_nodal_loads)

                for component in part.Components:
                    if isinstance(component, Brick):
                        self.__applybrickmass(component, loadpattern, sfactor, all_nodal_loads)

                    elif isinstance(component, Point):
                        self.__applypointmass(component, loadpattern, sfactor, all_nodal_loads)

                for el in nodeloads:
                    pat = el[0]
                    xyz = el[1]
                    values = el[2]
                    dirs = el[3]


                    if values == 0:
                        continue

                    if pat == loadpattern:
                        tag = self.__nodeexist_dict(xyz, part.getNodes())
                        if tag != False:
                            vals = np.zeros(_ndf, dtype=float)
                            vals[np.array(dirs) - 1] = values * sfactor
                            self.__add_nodeload(tag, list(vals), all_nodal_loads)

        for i in range(len(loadpatterns)):
            loadpattern = loadpatterns[i]
            sfactor = factors[i]
            nodeloads = self.NodalLoads
            for el in nodeloads:
                pat = el[0]
                xyz = el[1]
                values = el[2]
                dirs = el[3]

                if values == 0:
                    continue
                if pat == loadpattern:
                    tag = self.__nodeexist_dict(xyz, self.getNodes())
                    if tag != False:
                        vals = np.zeros(_ndf, dtype=float)
                        vals[np.array(dirs) - 1] = values * sfactor
                        self.__add_nodeload(tag, list(vals), all_nodal_loads)

        self.__assign_mass(g, mass_concentrate, mass_additional,  print_command, all_nodal_loads, n_mass, minval)

    def __applybrickloads(self, component, loadpattern, all_nodal_loads_patt):
        ops = self.ops
        sfactor = loadpattern['scalefactor']
        if len(component.Surfload) != 0:
            for lo in component.Surfload:
                if lo[0] == loadpattern:
                    face = lo[1]
                    fnodes = component.NodeSets[face]['Nodes']
                    Njk, Nij = len(fnodes), len(fnodes[0])
                    for i in range(Njk - 1):
                        for j in range(Nij - 1):
                            node_s = []
                            node_s.append(fnodes[i][j])
                            node_s.append(fnodes[i][j + 1])
                            node_s.append(fnodes[i + 1][j + 1])
                            node_s.append(fnodes[i + 1][j])
                            xyzi = ops.nodeCoord(node_s[0])
                            xyzj = ops.nodeCoord(node_s[1])
                            xyzk = ops.nodeCoord(node_s[2])
                            xyzl = ops.nodeCoord(node_s[3])
                            lo_ = [lo[0], lo[2], lo[3], lo[4]]
                            W_l, W_g = self.__quadnodalloads(xyzi, xyzj, xyzk, xyzl, lo_)


                            for k in range(4):
                                str_tag = str(node_s[k])
                                wx, wy, wz = list(W_g[k])
                                self.__add_nodeload_patt(loadpattern, node_s[k], list(W_g[k]), all_nodal_loads_patt)

                                # str_wx, str_wy, str_wz = str(wx * sfactor), str(wy * sfactor), str(wz * sfactor)
                                # str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ")"
                                # if print_command.lower() in ['y', 'yes']:
                                #     print(str_command)
                                #
                                # eval(str_command)
                                # file_loading.write(str_command + '\n')

        if len(component.Bodyload) != 0:
            for lo in component.Bodyload:
                if lo[0] == loadpattern:
                    elements = component.Elements
                    for ele in elements.keys():
                        node_s = elements[ele]
                        xyz1 = ops.nodeCoord(node_s[0])
                        xyz2 = ops.nodeCoord(node_s[1])
                        xyz3 = ops.nodeCoord(node_s[2])
                        xyz4 = ops.nodeCoord(node_s[3])
                        xyz5 = ops.nodeCoord(node_s[4])
                        xyz6 = ops.nodeCoord(node_s[5])
                        xyz7 = ops.nodeCoord(node_s[6])
                        xyz8 = ops.nodeCoord(node_s[7])
                        W_g = self.__bricknodalloads(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, lo)

                        for k in range(8):
                            str_tag = str(node_s[k])
                            wx, wy, wz = list(W_g[k])
                            self.__add_nodeload_patt(loadpattern, node_s[k], list(W_g[k]), all_nodal_loads_patt)
                            # str_wx, str_wy, str_wz = str(wx * sfactor), str(wy * sfactor), str(wz * sfactor)
                            # str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ")"
                            #
                            # if print_command.lower() in ['y', 'yes']:
                            #     print(str_command)
                            #
                            # eval(str_command)
                            # file_loading.write(str_command + '\n')

    def __applypointloads(self, component, loadpattern, all_nodal_loads_patt):
        _ndf = self.Ndf
        ops = self.ops
        tag = component.NodeTag
        for lo in component.Pointload:
            pat = lo[0]

            if pat == loadpattern:
                val = lo[1]
                dir = lo[2]
                vals = list(np.zeros(_ndf, dtype=int))
                vals[dir - 1] = val
                self.__add_nodeload_patt(loadpattern, tag, vals, all_nodal_loads_patt)

                # strvals = " "
                # if len(vals) != 0:
                #     for f in vals:
                #         strvals += ", " + str(f)
                #
                #     str_command = "ops.load(" + str(tag) + strvals + ")"
                #     if print_command.lower() in ['y', 'yes']:
                #         print(str_command)
                #
                #     eval(str_command)
                #
                #     file_loading.write(str_command + '\n')

    def apply_loads(self, *patterns, parts=[], print_command='n'):
        ops = self.ops
        _ndm = self.Ndm
        _ndf = self.Ndf
        _name = self.Name

        if len(parts) == 0:
            parts = self.Parts

        patterns = list(patterns)

        for loadpattern in patterns:
            all_nodal_loads_patt = []
            all_line_loads_patt = []
            print('# Applying Loads: ', loadpattern['Name'])

            file_loading = open(_name + "\\" + "file_loading_" + loadpattern['Name'] + ".txt", "a")
            file_loading.write("# " + loadpattern['Name'] + '\n')
            str_timeser = str(loadpattern['tsTag'])
            sfactor = loadpattern['scalefactor']
            pattag = loadpattern['Tag']
            str_command = "ops.pattern(" + "\'" + loadpattern['Type'] + "\'" + ", " + str(pattag) + ", " + str_timeser + ")"

            if print_command.lower() in ['y', 'yes']:
                print(str_command)
            file_loading.write(str_command + '\n')
            eval(str_command)

            for part in parts:
                lineuniloads = part.LineUniLoads
                quaduniloads = part.QuadUniLoads
                nodeloads = part.NodalLoads

                # eleLoad('-ele', '-type', '-beamUniform', Wy, <Wz>, Wx=0.0)
                for el in lineuniloads.keys():
                    if len(lineuniloads[el]) != 0:
                        for lo in lineuniloads[el]:
                            if len(lo) != 0:
                                if lo[0] == loadpattern:
                                    if _ndm == 2:
                                        wx = wy = wz = 0.0
                                        if lo[2] == 1:
                                            wx = lo[1]
                                        elif lo[2] == 2:
                                            wy = lo[1]
                                        else:
                                            raise ValueError('beam uniform loading: ndm = 2 ==> direction should be 1 or 2')
                                    else:
                                        wx = wy = wz = 0.0
                                        if lo[2] == 1:
                                            wx = lo[1]
                                        elif lo[2] == 2:
                                            wy = lo[1]
                                        elif lo[2] == 3:
                                            wz = lo[1]
                                        else:
                                            raise ValueError(
                                                'beam uniform loading: ndm = 3 ==> direction should be 1, 2 or 3')


                                        if lo[3].lower() in ['g', 'global']:
                                            comp = self.__find_component(el, part)
                                            if comp != None:
                                                wx, wy, wz = self.__load_transe_g2l(comp, el, [wx, wy, wz])

                                        self.__add_lineload_patt(loadpattern, el, [wx, wy, wz], all_line_loads_patt)

                                    # str_eletag = str(el)
                                    # if _ndm == 2:
                                    #     self.__add_lineload_patt(loadpattern, el, [wx, wy], all_line_loads_patt)
                                        # str_wx, str_wy = str(wx * sfactor), str(wy * sfactor)
                                        # str_command = "ops.eleLoad('-ele', " + str_eletag + ", '-type', '-beamUniform', " + \
                                        #               str_wy + ", " + str_wx + ")"
                                    # else:
                                    #     self.__add_lineload_patt(loadpattern, el, [wx, wy, wz], all_line_loads_patt)
                                        # str_wx, str_wy, str_wz = str(wx), str(wy * sfactor), str(wz * sfactor)
                                        # str_command = "ops.eleLoad('-ele', " + str_eletag + ", '-type', '-beamUniform', " + \
                                        #               str_wy + ", " + str_wz + ", " + str_wx + ")"

                                    # if print_command.lower() in ['y', 'yes']:
                                    #     print(str_command)
                                    #
                                    # eval(str_command)
                                    # file_loading.write(str_command + '\n')

                # load(nodeTag, *loadValues)
                for el in quaduniloads.keys():
                    if len(quaduniloads[el]) != 0:
                        for lo in quaduniloads[el]:
                            if len(lo) != 0:
                                if lo[0] == loadpattern:
                                    ele_nodes = ops.eleNodes(el)
                                    if len(ele_nodes) == 3:
                                        xyzi = ops.nodeCoord(ele_nodes[0])
                                        xyzj = ops.nodeCoord(ele_nodes[1])
                                        xyzk = ops.nodeCoord(ele_nodes[2])

                                        if len(xyzi) == 2:
                                            xyzi.append(0.0)
                                            xyzj.append(0.0)
                                            xyzk.append(0.0)

                                        W_l, W_g = self.__trinodalloads(xyzi, xyzj, xyzk, lo)

                                        for i in range(3):
                                            self.__add_nodeload_patt(loadpattern, ele_nodes[i], list(W_g[i]), all_nodal_loads_patt)
                                            # if _ndm == 3:
                                            #     str_wx, str_wy, str_wz = str(wx * sfactor), str(wy * sfactor), str(
                                            #         wz * sfactor)
                                            #     if _ndf == 2:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ")"
                                            #     elif _ndf == 3:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ")"
                                            #     elif _ndf == 6:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ", 0.0, 0.0, 0.0)"
                                            #
                                            # else:
                                            #     str_wx, str_wy = str(wx * sfactor), str(wy * sfactor)
                                            #     if _ndf == 3:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", 0.0)"
                                            #     elif _ndf == 2:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ")"
                                            #
                                            # if print_command.lower() in ['y', 'yes']:
                                            #     print(str_command)
                                            #
                                            # eval(str_command)
                                            # file_loading.write(str_command + '\n')

                                    elif len(ele_nodes) == 4:
                                        xyzi = ops.nodeCoord(ele_nodes[0])
                                        xyzj = ops.nodeCoord(ele_nodes[1])
                                        xyzk = ops.nodeCoord(ele_nodes[2])
                                        xyzl = ops.nodeCoord(ele_nodes[3])
                                        if len(xyzi) == 2:
                                            xyzi.append(0.0)
                                            xyzj.append(0.0)
                                            xyzk.append(0.0)
                                            xyzl.append(0.0)

                                        W_l, W_g = self.__quadnodalloads(xyzi, xyzj, xyzk, xyzl, lo)

                                        for i in range(4):
                                            self.__add_nodeload_patt(loadpattern, ele_nodes[i], list(W_g[i]), all_nodal_loads_patt)
                                            # if _ndm == 3:
                                            #     str_wx, str_wy, str_wz = str(wx * sfactor), str(wy * sfactor), str(
                                            #         wz * sfactor)
                                            #     if _ndf == 2:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ")"
                                            #     elif _ndf == 3:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ")"
                                            #     elif _ndf == 6:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ", 0.0, 0.0, 0.0)"
                                            #
                                            # else:
                                            #     str_wx, str_wy = str(wx * sfactor), str(wy * sfactor)
                                            #     if _ndf == 3:
                                            #          str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", 0.0)"
                                            #     elif _ndf ==2:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ")"
                                            #
                                            # if print_command.lower() in ['y', 'yes']:
                                            #     print(str_command)
                                            #
                                            # eval(str_command)
                                            # file_loading.write(str_command + '\n')

                                    elif len(ele_nodes) == 9:
                                        xyz1 = ops.nodeCoord(ele_nodes[0])
                                        xyz2 = ops.nodeCoord(ele_nodes[1])
                                        xyz3 = ops.nodeCoord(ele_nodes[2])
                                        xyz4 = ops.nodeCoord(ele_nodes[3])
                                        xyz5 = ops.nodeCoord(ele_nodes[4])
                                        xyz6 = ops.nodeCoord(ele_nodes[5])
                                        xyz7 = ops.nodeCoord(ele_nodes[6])
                                        xyz8 = ops.nodeCoord(ele_nodes[7])
                                        xyz9 = ops.nodeCoord(ele_nodes[8])
                                        if len(xyz1) == 2:
                                            xyz1.append(0.0)
                                            xyz2.append(0.0)
                                            xyz3.append(0.0)
                                            xyz4.append(0.0)
                                            xyz5.append(0.0)
                                            xyz6.append(0.0)
                                            xyz7.append(0.0)
                                            xyz8.append(0.0)
                                            xyz9.append(0.0)
                                        W_l, W_g = self.__quad9nodalloads(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7,
                                                                          xyz8, xyz9, lo)

                                        for i in range(9):
                                            self.__add_nodeload_patt(loadpattern, ele_nodes[i], list(W_g[i]),
                                                                     all_nodal_loads_patt)
                                            # if _ndm == 3:
                                            #     str_wx, str_wy, str_wz = str(wx * sfactor), str(wy * sfactor), str(
                                            #         wz * sfactor)
                                            #     if _ndf == 2:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ")"
                                            #     elif _ndf == 3:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ")"
                                            #     elif _ndf == 6:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", " + str_wz + ", 0.0, 0.0, 0.0)"
                                            #
                                            # else:
                                            #     str_wx, str_wy = str(wx * sfactor), str(wy * sfactor)
                                            #     if _ndf == 3:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ", 0.0)"
                                            #     elif _ndf == 2:
                                            #         str_command = "ops.load(" + str_tag + ", " + str_wx + ", " + str_wy + ")"
                                            #
                                            # if print_command.lower() in ['y', 'yes']:
                                            #     print(str_command)
                                            #
                                            # eval(str_command)
                                            # file_loading.write(str_command + '\n')

                for component in part.Components:
                    if isinstance(component, Brick):
                        self.__applybrickloads(component, loadpattern, all_nodal_loads_patt)

                    elif isinstance(component, Point):
                        self.__applypointloads(component, loadpattern, all_nodal_loads_patt)

                for el in nodeloads:
                    pat = el[0]
                    xyz = el[1]
                    values = el[2]
                    dirs = el[3]

                    if values == 0:
                        continue

                    if pat == loadpattern:
                        tag = nodeexist(ops, xyz)
                        if tag != False:
                            vals = np.zeros(_ndf, dtype=float)
                            vals[np.array(dirs) - 1] = values
                            self.__add_nodeload_patt(loadpattern, tag, list(vals), all_nodal_loads_patt)

            nodeloads = self.NodalLoads
            for el in nodeloads:
                pat = el[0]
                xyz = el[1]
                values = el[2]
                dirs = el[3]

                if values == 0:
                    continue

                if pat == loadpattern:
                    tag = nodeexist(ops, xyz)
                    if tag != False:
                        vals = np.zeros(_ndf, dtype=float)
                        vals[np.array(dirs) - 1] = values
                        self.__add_nodeload_patt(loadpattern, tag, list(vals), all_nodal_loads_patt)

            self.__assign_nodal_loads(print_command, sfactor, file_loading, all_nodal_loads_patt)
            self.__assign_line_loads(print_command, sfactor, file_loading, all_line_loads_patt)
            file_loading.close()
            print('# Applying Loads: ', loadpattern['Name'], 'Done')

    def add_geomTransf(self, *geomTransfs):
        if isinstance(geomTransfs, geomTransf):
            self.geomTransf.append(geomTransfs)
        elif isinstance(geomTransfs, list) or isinstance(geomTransfs, tuple):
            for tr in geomTransfs:
                self.geomTransf.append(tr)
        else:
            raise TypeError('geomTransfs must be a geomTransf or list of geomTransfs')

    def __addmass(self, part, n_mass):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name
        if part is None:
            no_masses = self.NodalMasses
            nodes = self.getNodes()
        else:
            no_masses = part.NodalMasses
            nodes = part.getNodes()
        for el in no_masses:
            xyz = el[0]
            value = el[1]
            dir = el[2]

            if value == 0:
                continue
            tag = self.__nodeexist_dict(xyz, nodes)

            if tag is not False:
                vals = np.zeros(_ndf, dtype=float)
                vals[np.array(dir) - 1] = value
                if n_mass.get(tag) is None:
                    n_mass[tag] = vals
                else:
                    n_mass[tag] += vals


    def __assignrest(self, nodetag, cvals, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name

        str_vals = ""
        cvals_ = np.zeros(_ndf)
        cvals_[np.array(cvals) - 1] = 1
        for m in cvals_:
            str_vals += ", " + str(m)

        file_fix = open(_name + "\\" + "file_fix.txt", "a")

        str_command = "ops.fix(" + str(nodetag) + str_vals + ")"
        file_fix.write(str_command + '\n')

        if print_command.lower() in ['y', 'yes']:
            print(str_command)

        eval(str_command)
        file_fix.close()

    def __nodeexist_dict(self, xyz, benodes):
        _ndm = self.Ndm
        _tolerance = self.Tolerance

        if _ndm == 3:
            x, y, z = xyz
        elif _ndm == 2:
            x, y = xyz[0], xyz[1]
            z = 0
        exist = False

        for nod in benodes.keys():
            if _ndm == 3:
                xn, yn, zn = benodes[nod]
            elif _ndm == 2:
                xn, yn = benodes[nod]
                zn = 0

            if (abs(x - xn) + abs(y - yn) + abs(z - zn)) < _tolerance:
                exist = nod
                break
        return exist

    def __nodeexist(self, xyz, benodes):
        _ndm = self.Ndm
        _tolerance = self.Tolerance

        if _ndm == 3:
            x, y, z = xyz
        elif _ndm == 2:
            x, y = xyz[0], xyz[1]
            z = 0
        exist = False

        for nod in benodes:
            if _ndm == 3:
                xn, yn, zn = nod[1], nod[2], nod[3]
            elif _ndm == 2:
                xn, yn = nod[1], nod[2]
                zn = 0

            if (abs(x - xn) + abs(y - yn) + abs(z - zn)) < _tolerance:
                exist = nod[0]
                break
        return exist

    def __assignspconstraint(self, part, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name

        nodes = list(part.getNodes().keys())
        for spconsts in part.SpConstraints:

            xlim, ylim, zlim, dirs = spconsts[0], spconsts[1], spconsts[2], spconsts[3]

            if len(xlim) == 2:
                check_x = True
            elif len(xlim) == 0:
                check_x = False
            else:
                raise ValueError('xlim should be an empty list or a list with xmin and xmax values')

            if len(ylim) == 2:
                check_y = True
            elif len(ylim) == 0:
                check_y = False
            else:
                raise ValueError('ylim should be an empty list or a list with ymin and ymax values')

            if len(zlim) == 2:
                check_z = True
            elif len(zlim) == 0:
                check_z = False
            else:
                raise ValueError('zlim should be an empty list or a list with zmin and zmax values')

            if len(dirs) == 0:
                dirs = list(np.arange(1, _ndf + 1, dtype=int))

            cvals = list(np.zeros(_ndf, dtype=int))
            for n in dirs:
                cvals[n - 1] = 1

            str_vals = ""
            for m in cvals:
                str_vals += ", " + str(m)

            file_fix = open(_name + "\\" + "file_fix.txt", "a")
            node_s = find_nodes_dict(part.getNodes(), xlim, ylim, zlim)
            if node_s is False:
                return

            for nod in node_s:
                str_command = "ops.fix(" + str(nod) + str_vals + ")"
                file_fix.write(str_command + '\n')

                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)

            file_fix.close()
    def __assignspconstraint_model(self, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name

        for spconsts in self.SpConstraints:

            parts, xlim, ylim, zlim, dirs = spconsts[0], spconsts[1], spconsts[2], spconsts[3], spconsts[4]

            if len(xlim) == 2:
                check_x = True
            elif len(xlim) == 0:
                check_x = False
            else:
                raise ValueError('xlim should be an empty list or a list with xmin and xmax values')

            if len(ylim) == 2:
                check_y = True
            elif len(ylim) == 0:
                check_y = False
            else:
                raise ValueError('ylim should be an empty list or a list with ymin and ymax values')

            if len(zlim) == 2:
                check_z = True
            elif len(zlim) == 0:
                check_z = False
            else:
                raise ValueError('zlim should be an empty list or a list with zmin and zmax values')

            if len(dirs) == 0:
                dirs = list(np.arange(1, _ndf + 1, dtype=int))

            cvals = list(np.zeros(_ndf, dtype=int))
            for n in dirs:
                cvals[n - 1] = 1

            str_vals = ""
            for m in cvals:
                str_vals += ", " + str(m)

            file_fix = open(_name + "\\" + "file_fix.txt", "a")
            node_s = find_nodes_dict(self.getNodes(parts), xlim, ylim, zlim)
            if node_s is False:
                return

            for nod in node_s:
                str_command = "ops.fix(" + str(nod) + str_vals + ")"
                file_fix.write(str_command + '\n')

                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)

            file_fix.close()

    def __assignrigidlink(self, part, rigidlink, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name
        nodes = part.getNodes()
        xyzr, type, xlim, ylim, zlim = rigidlink[0], rigidlink[1], rigidlink[2], rigidlink[3], rigidlink[4]

        if len(xlim) == 2:
            check_x = True
        elif len(xlim) == 0:
            check_x = False
        else:
            raise ValueError('xlim should be an empty list or a list with xmin and xmax values')

        if len(ylim) == 2:
            check_y = True
        elif len(ylim) == 0:
            check_y = False
        else:
            raise ValueError('ylim should be an empty list or a list with ymin and ymax values')

        if len(zlim) == 2:
            check_z = True
        elif len(zlim) == 0:
            check_z = False
        else:
            raise ValueError('zlim should be an empty list or a list with zmin and zmax values')

        noder = self.__nodeexist_dict(xyzr, nodes)
        if noder is False:
            print("Note:")
            print("rigidLink constraint: Master node was not found")
            return

        for nod in nodes.keys():
            if _ndm == 3:
                xn, yn, zn = nodes[nod]
            elif _ndm == 2:
                xn, yn = nodes[nod]
                check_z = False

            if nod == noder:
                continue

            if check_x:
                if xn < xlim[0] or xn > xlim[1]:
                    continue

            if check_y:
                if yn < ylim[0] or yn > ylim[1]:
                    continue

            if check_z:
                if zn < zlim[0] or zn > zlim[1]:
                    continue
            # rigidLink(type, rNodeTag, cNodeTag)
            if noder != nod:
                if type == 'beam':
                    str_command = "ops.rigidLink('beam', " + str(noder) + ", " + str(nod) + ")"
                elif type == 'bar':
                    str_command = "ops.rigidLink('bar', " + str(noder) + ", " + str(nod) + ")"

                file_constraint = open(_name + "\\" + "file_constraint.txt", "a")
                file_constraint.write(str_command + '\n')

                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)
                file_constraint.close()

    def __assignrigidlink_model(self, rigidlink, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name

        parts, xyzr, type, xlim, ylim, zlim = rigidlink[0], rigidlink[1], rigidlink[2], rigidlink[3], rigidlink[4], rigidlink[5]
        nodes = self.getNodes(parts)
        if len(xlim) == 2:
            check_x = True
        elif len(xlim) == 0:
            check_x = False
        else:
            raise ValueError('xlim should be an empty list or a list with xmin and xmax values')

        if len(ylim) == 2:
            check_y = True
        elif len(ylim) == 0:
            check_y = False
        else:
            raise ValueError('ylim should be an empty list or a list with ymin and ymax values')

        if len(zlim) == 2:
            check_z = True
        elif len(zlim) == 0:
            check_z = False
        else:
            raise ValueError('zlim should be an empty list or a list with zmin and zmax values')

        noder = self.__nodeexist_dict(xyzr, nodes)
        if noder is False:
            print("Note:")
            print("rigidLink constraint: Master node was not found")
            return

        for nod in nodes.keys():
            if _ndm == 3:
                xn, yn, zn = nodes[nod]
            elif _ndm == 2:
                xn, yn = nodes[nod]
                check_z = False

            if nod == noder:
                continue

            if check_x:
                if xn < xlim[0] or xn > xlim[1]:
                    continue

            if check_y:
                if yn < ylim[0] or yn > ylim[1]:
                    continue

            if check_z:
                if zn < zlim[0] or zn > zlim[1]:
                    continue
            # rigidLink(type, rNodeTag, cNodeTag)
            if noder != nod:
                if type == 'beam':
                    str_command = "ops.rigidLink('beam', " + str(noder) + ", " + str(nod) + ")"
                elif type == 'bar':
                    str_command = "ops.rigidLink('bar', " + str(noder) + ", " + str(nod) + ")"

                file_constraint = open(_name + "\\" + "file_constraint.txt", "a")
                file_constraint.write(str_command + '\n')

                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)
                file_constraint.close()

    def __assignequaldof(self, part, equaldof, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name
        nodes = part.getNodes()

        xyzr, xlim, ylim, zlim, dofs = equaldof[0], equaldof[1], equaldof[2], equaldof[3], equaldof[4]
        if len(xlim) == 2:
            check_x = True
        elif len(xlim) == 0:
            check_x = False
        else:
            raise ValueError('xlim should be an empty list or a list with xmin and xmax values')

        if len(ylim) == 2:
            check_y = True
        elif len(ylim) == 0:
            check_y = False
        else:
            raise ValueError('ylim should be an empty list or a list with ymin and ymax values')

        if len(zlim) == 2:
            check_z = True
        elif len(zlim) == 0:
            check_z = False
        else:
            raise ValueError('zlim should be an empty list or a list with zmin and zmax values')

        # equalDOF(rNodeTag, cNodeTag, *dofs)
        if len(dofs) == 0:
            dofs = list(np.arange(1, _ndf + 1, dtype=int))

        str_vals = ""
        for d in dofs:
            str_vals = str_vals + ", " + str(int(d))

        noder = self.__nodeexist_dict(xyzr, nodes)
        if noder is False:
            print("# Note:")
            print("# eualDof constraint: Master node was not found")
            return

        for nod in nodes.keys():
            if _ndm == 3:
                xn, yn, zn = nodes[nod]
            elif _ndm == 2:
                xn, yn = nodes[nod]
                check_z = False

            if nod == noder:
                continue

            if check_x:
                if xn < xlim[0] or xn > xlim[1]:
                    continue

            if check_y:
                if yn < ylim[0] or yn > ylim[1]:
                    continue

            if check_z:
                if zn < zlim[0] or zn > zlim[1]:
                    continue
            if noder != nod:
                str_command = "ops.equalDOF(" + str(noder) + ", " + str(nod) + str_vals + ")"

                file_constraint = open(_name + "\\" + "file_constraint.txt", "a")
                file_constraint.write(str_command + '\n')

                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)
                file_constraint.close()

    def __assignequaldof_model(self, equaldof, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name


        parts, xyzr, xlim, ylim, zlim, dofs = equaldof[0], equaldof[1], equaldof[2], equaldof[3], equaldof[4], equaldof[5]
        nodes = self.getNodes(parts)
        if len(xlim) == 2:
            check_x = True
        elif len(xlim) == 0:
            check_x = False
        else:
            raise ValueError('xlim should be an empty list or a list with xmin and xmax values')

        if len(ylim) == 2:
            check_y = True
        elif len(ylim) == 0:
            check_y = False
        else:
            raise ValueError('ylim should be an empty list or a list with ymin and ymax values')

        if len(zlim) == 2:
            check_z = True
        elif len(zlim) == 0:
            check_z = False
        else:
            raise ValueError('zlim should be an empty list or a list with zmin and zmax values')

        # equalDOF(rNodeTag, cNodeTag, *dofs)
        if len(dofs) == 0:
            dofs = list(np.arange(1, _ndf + 1, dtype=int))

        str_vals = ""
        for d in dofs:
            str_vals = str_vals + ", " + str(int(d))

        noder = self.__nodeexist_dict(xyzr, nodes)
        if noder is False:
            print("# Note:")
            print("# eualDof constraint: Master node was not found")
            return

        for nod in nodes.keys():
            if _ndm == 3:
                xn, yn, zn = nodes[nod]
            elif _ndm == 2:
                xn, yn = nodes[nod]
                check_z = False

            if nod == noder:
                continue

            if check_x:
                if xn < xlim[0] or xn > xlim[1]:
                    continue

            if check_y:
                if yn < ylim[0] or yn > ylim[1]:
                    continue

            if check_z:
                if zn < zlim[0] or zn > zlim[1]:
                    continue

            if noder != nod:
                str_command = "ops.equalDOF(" + str(noder) + ", " + str(nod) + str_vals + ")"

                file_constraint = open(_name + "\\" + "file_constraint.txt", "a")
                file_constraint.write(str_command + '\n')

                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)
                file_constraint.close()

    def __assignrigiddiaph(self, part, rigiddiaph, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name

        nodes = part.getNodes()

        xyzr, perpdirn = rigiddiaph[0], rigiddiaph[1]
        xlim, ylim, zlim, massr, rests = rigiddiaph[2], rigiddiaph[3], rigiddiaph[4], rigiddiaph[5], rigiddiaph[6]
        if len(xlim) == 2:
            check_x = True
        elif len(xlim) == 0:
            check_x = False
        else:
            raise ValueError('xlim should be an empty list or a list with xmin and xmax values')

        if len(ylim) == 2:
            check_y = True
        elif len(ylim) == 0:
            check_y = False
        else:
            raise ValueError('ylim should be an empty list or a list with ymin and ymax values')

        if len(zlim) == 2:
            check_z = True
        elif len(zlim) == 0:
            check_z = False
        else:
            raise ValueError('zlim should be an empty list or a list with zmin and zmax values')

        if not isinstance(xyzr, str):
            noder = self.__nodeexist_dict(xyzr, self.getNodes())
            file_constraint = open(_name + "\\" + "file_constraint.txt", "a")
            warnnote = ""
            if noder is False:
                warnnote = "# Rigid Diaphragm constraint: Master node was not found. A new node was created as master node"
                print("# Note:")
                print(warnnote)
                rnode = create_node(ops, xyzr, print_command)
                if len(rests) != 0:
                    file_fix = open(_name + "\\" + "file_fix.txt", "a")
                    restvals = list(np.zeros(_ndf, dtype=int))
                    for rs in rests:
                        restvals[rs - 1] = 1

                    str_vals = ""
                    for rsv in restvals:
                        str_vals = str_vals + ", " + str(rsv)

                    str_command = "ops.fix(" + str(rnode) + str_vals + ")"

                    file_fix.write(str_command + '\n')

                    if print_command.lower() in ['y', 'yes']:
                        print(str_command)
                    eval(str_command)
                    file_fix.close()

            else:
                rnode = noder

            cnodes = self.MassCenters
            cnodes.update({rnode: xyzr})
            self.MassCenters = cnodes
        else:
            rnode = xyzr

        cNodeTags = []
        for nod in nodes.keys():
            if _ndm == 3:
                xn, yn, zn = nodes[nod]
            elif _ndm == 2:
                xn, yn = nodes[nod]
                check_z = False

            if nod == rnode:
                continue

            if check_x:
                if xn < xlim[0] or xn > xlim[1]:
                    continue

            if check_y:
                if yn < ylim[0] or yn > ylim[1]:
                    continue

            if check_z:
                if zn < zlim[0] or zn > zlim[1]:
                    continue
            cNodeTags.append(nod)

            str_cnodes = ""
            for n in cNodeTags:
                if n != rnode:
                    str_cnodes = str_cnodes + ", " + str(n)

        if len(cNodeTags) != 0:
            self.createdRgDiapgh.append([rnode, cNodeTags, massr, rests, perpdirn])
            if not isinstance(xyzr, str):
                str_command = "ops.rigidDiaphragm(" + str(perpdirn) + ", " + str(rnode) + str_cnodes + ")"

                file_constraint.write(warnnote + '\n')
                file_constraint.write(str_command + '\n')
                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)
                file_constraint.close()

    def __assignrigiddiaph_model(self, rigiddiaph, print_command):
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name

        parts, xyzr, perpdirn = rigiddiaph[0], rigiddiaph[1], rigiddiaph[2]
        xlim, ylim, zlim, massr, rests = rigiddiaph[3], rigiddiaph[4], rigiddiaph[5], rigiddiaph[6], rigiddiaph[7]
        nodes = self.getNodes(parts)
        if len(xlim) == 2:
            check_x = True
        elif len(xlim) == 0:
            check_x = False
        else:
            raise ValueError('xlim should be an empty list or a list with xmin and xmax values')

        if len(ylim) == 2:
            check_y = True
        elif len(ylim) == 0:
            check_y = False
        else:
            raise ValueError('ylim should be an empty list or a list with ymin and ymax values')

        if len(zlim) == 2:
            check_z = True
        elif len(zlim) == 0:
            check_z = False
        else:
            raise ValueError('zlim should be an empty list or a list with zmin and zmax values')
        if not isinstance(xyzr, str):
            noder = self.__nodeexist_dict(xyzr, self.getNodes())
            file_constraint = open(_name + "\\" + "file_constraint.txt", "a")
            warnnote = ""
            if noder is False:
                warnnote = "# Rigid Diaphragm constraint: Master node was not found. A new node was created as master node"
                print("# Note:")
                print(warnnote)
                rnode = create_node(ops, xyzr, print_command)
                if len(rests) != 0:
                    file_fix = open(_name + "\\" + "file_fix.txt", "a")
                    restvals = list(np.zeros(_ndf, dtype=int))
                    for rs in rests:
                        restvals[rs - 1] = 1

                    str_vals = ""
                    for rsv in restvals:
                        str_vals = str_vals + ", " + str(rsv)

                    str_command = "ops.fix(" + str(rnode) + str_vals + ")"

                    file_fix.write(str_command + '\n')

                    if print_command.lower() in ['y', 'yes']:
                        print(str_command)
                    eval(str_command)
                    file_fix.close()

            else:
                rnode = noder

            cnodes = self.MassCenters
            cnodes.update({rnode: xyzr})
            self.MassCenters = cnodes
        else:
            rnode = xyzr

        cNodeTags = []
        for nod in nodes.keys():
            if _ndm == 3:
                xn, yn, zn = nodes[nod]
            elif _ndm == 2:
                xn, yn = nodes[nod]
                check_z = False

            if nod == rnode:
                continue

            if check_x:
                if xn < xlim[0] or xn > xlim[1]:
                    continue

            if check_y:
                if yn < ylim[0] or yn > ylim[1]:
                    continue

            if check_z:
                if zn < zlim[0] or zn > zlim[1]:
                    continue
            cNodeTags.append(nod)

            str_cnodes = ""
            for n in cNodeTags:
                if n != rnode:
                    str_cnodes = str_cnodes + ", " + str(n)

        if len(cNodeTags) != 0:
            self.createdRgDiapgh.append([rnode, cNodeTags, massr, rests, perpdirn])
            if not isinstance(xyzr, str):
                str_command = "ops.rigidDiaphragm(" + str(perpdirn) + ", " + str(rnode) + str_cnodes + ")"

                file_constraint.write(warnnote + '\n')
                file_constraint.write(str_command + '\n')
                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)
                file_constraint.close()

    def __create_geomTransf(self, gtrans, print_command='n'):
        ops = self.ops
        if type(print_command) != str:
            raise ValueError('mergenodes must be \'y\', \'yes\',\'n\' or \'no\'')

        str_com = gtrans.create_command()
        if print_command.lower() in ['y', 'yes']:
            print(str_com)
        eval(str_com)

    def plot_model(self, ax, name='n', propname='y', subdivisions='y', localcoord='n', linewidth=0.2, pointsize=0.2,
                   edgelinewidth=0.3, fill='y',  coloring='eleProps', legend='y', fontsize=3, xlim=[], ylim=[], zlim=[],
                   facenumber='n', alpha=0.5):

        parts = self.Parts
        plot_parts(*parts, ax=ax, name=name, propname=propname, subdivisions=subdivisions, localcoord=localcoord, linewidth=linewidth,
                   pointsize=pointsize, edgelinewidth=edgelinewidth, fill=fill, coloring=coloring, legend=legend, fontsize=fontsize,
                   xlim=xlim, ylim=ylim, zlim=zlim, facenumber=facenumber, alpha=alpha)

        # x_min, x_max = ax.get_xlim()
        # y_min, y_max = ax.get_ylim()
        #
        # X = np.linspace(x_min, x_max, 10)
        # Y = np.linspace(y_min, y_max, 10)
        # X, Y = np.meshgrid(X, Y)
        # Z = np.sqrt(X * 0)
        # surf = ax.plot_surface(X, Y, Z, alpha=0.1, linewidth=0.1, linestyle='--',  antialiased=False, facecolor='0.9',
        #                        edgecolor='0.87', shade=False)

    def create_opsmodel(self, parts=[], print_command='n'):
        global _parts
        ops = self.ops
        _ndf = self.Ndf
        _ndm = self.Ndm
        _name = self.Name
        if len(parts) == 0:
            parts = self.Parts

        self.CreatedParts = parts

        ptag = 1
        for pa in parts:
            pa.Tag = ptag
            ptag += 1

        geoTr = self.geomTransf
        gtag = 1
        for tr in geoTr:
            tr.Tag = gtag
            self.__create_geomTransf(tr, print_command)
            gtag += 1

        _parts = parts

        if type(print_command) != str:
            raise ValueError('print_command must be \'y\', \'yes\',\'n\' or \'no\'')

        if print_command.lower() not in ['y', 'yes', 'n', 'no']:
            raise ValueError('print_command must be \'y\', \'yes\',\'n\' or \'no\'')

        if os.path.exists(_name):
            shutil.rmtree(_name)
        os.mkdir(_name)

        file_elements = open(_name + "\\" + "file_elements.txt", "a")
        print('# Create Opensees Model: ', self.Name)
        output = {}
        models_attached = []
        models_notattached = []
        for part in parts:
            if part.Attach.lower() in ['y', 'yes']:
                models_attached.append(part)
            else:
                models_notattached.append(part)

        for part in models_attached:
            for component in part.Components:
                if len(ops.getNodeTags()) == 0:
                    nodeTag = 0
                else:
                    nodeTag = int(np.max(ops.getNodeTags()))

                if isinstance(component, Point):
                    x, y, z = component.XYZ
                    exnodeTag = nodeexist(ops, [x, y, z])
                    if exnodeTag is False:
                        if _ndm == 2:
                            str_command = "ops.node(" + str(int(1 + nodeTag)) + ", " + str(x) + ", " + str(y) + ")"

                        elif _ndm == 3:
                            str_command = "ops.node(" + str(int(1 + nodeTag)) + ", " + str(x) + ", " + str(y) + \
                                          ", " + str(z) + ")"

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)
                        component.NodeTag = 1 + nodeTag
                        component.Nodes = {1 + nodeTag: [x, y, z]}
                        if len(component.Rest) != 0:
                            self.__assignrest(1 + nodeTag, component.Rest, print_command)

                        if len(component.Mass) != 0:
                            cmass = component.Mass
                            for i  in range(len(cmass)):
                                part.assign_nodalmass([x, y, z], cmass[i], i + 1, 'a')
                        file_nodes = open(_name + "\\" + "file_nodes.txt", "a")
                        file_nodes.write(str_command + '\n')
                        file_nodes.close()
                    else:
                        component.NodeTag = exnodeTag

        for part in models_attached:
            file_elements.write('# Part: ' + part.Name + '\n')
            print('# Part: ', part.Name)

            lineuniloads = {}
            quaduniloads = {}
            bodyloads = {}

            components = part.Components
            for component in components:
                if len(ops.getNodeTags()) == 0:
                    nodeTag = 0
                else:
                    nodeTag = int(np.max(ops.getNodeTags()))

                if len(ops.getEleTags()) == 0:
                    eleTag = 0
                else:
                    eleTag = int(np.max(ops.getEleTags()))

                Nodesatsameloc = []
                exnodes = []

                if isinstance(component, Point):
                    continue

                Nodes, Elements, Noderange = component.createelements()
                eleProps = component.EleProps
                nodes_ = component.Nodes
                elements_ = component.Elements
                nodecounts = {}

                for tag in Nodes.keys():
                    x = Nodes[tag][0]
                    y = Nodes[tag][1]
                    z = Nodes[tag][2]
                    exnodeTag = nodeexist(ops, [x, y, z])
                    if exnodeTag is False:
                        nodecounts[tag] = tag + nodeTag
                        nodes_[tag + nodeTag] = [x, y, z]
                    else:
                        exnodes.append(exnodeTag)
                        nodecounts[tag] = exnodeTag
                        nodes_[exnodeTag] = [x, y, z]

                # Create Node Objects
                file_nodes = open(_name + "\\" + "file_nodes.txt", "a")
                for nod in nodes_.keys():
                    x, y, z = nodes_[nod]
                    if nod not in exnodes:
                        if _ndm == 2:
                            str_command = "ops.node(" + str(int(nod)) + ", " + str(x) + ", " + str(y) + ")"
                        elif _ndm == 3:
                            str_command = "ops.node(" + str(int(nod)) + ", " + str(x) + ", " + str(y) + ", " + str(
                                z) + ")"

                        file_nodes.write(str_command + '\n')

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)

                file_nodes.close()
                nodeset = component.NodeSets

                if isinstance(component, Brick):
                    for face in Noderange.keys():
                        fnodes = Noderange[face]['Nodes']
                        nfnodes = []
                        for nn in fnodes:
                            nfnodes_ = []
                            for n in nn:
                                nfnodes_.append(int(nodecounts[n]))

                            nfnodes.append(nfnodes_)

                        nodeset[face]['Nodes'] = nfnodes

                        fnodes = Noderange[face]['ij']
                        nfnodes_ = []
                        for nn in fnodes:
                            nfnodes_.append(int(nodecounts[nn]))

                        nodeset[face]['ij'] = nfnodes_

                        fnodes = Noderange[face]['jk']
                        nfnodes_ = []
                        for nn in fnodes:
                            nfnodes_.append(int(nodecounts[nn]))

                        nodeset[face]['jk'] = nfnodes_

                        fnodes = Noderange[face]['kl']
                        nfnodes_ = []
                        for nn in fnodes:
                            nfnodes_.append(int(nodecounts[nn]))

                        nodeset[face]['kl'] = nfnodes_

                        fnodes = Noderange[face]['li']
                        nfnodes_ = []
                        for nn in fnodes:
                            nfnodes_.append(int(nodecounts[nn]))

                        nodeset[face]['li'] = nfnodes_

                elif isinstance(component, Quad):

                    nodeset['ij'] = [nodecounts[x] for x in Noderange[0]]
                    nodeset['jk'] = [nodecounts[x] for x in Noderange[1]]
                    nodeset['kl'] = [nodecounts[x] for x in Noderange[2]]
                    nodeset['li'] = [nodecounts[x] for x in Noderange[3]]

                elif isinstance(component, Triangle):
                    nodeset['ij'] = [nodecounts[x] for x in Noderange[0]]
                    nodeset['jk'] = [nodecounts[x] for x in Noderange[1]]
                    nodeset['ki'] = [nodecounts[x] for x in Noderange[2]]
                elif isinstance(component, Polygon):
                    nrcount = 1
                    for node_r in Noderange:
                        nodeset[str(nrcount)] = [nodecounts[x] for x in node_r]
                        nrcount += 1
                elif isinstance(component, Line):
                    nodeset['i'] = nodecounts[Noderange[0]]
                    nodeset['j'] = nodecounts[Noderange[1]]

                if isinstance(component, Line):
                    for ele in Elements.keys():
                        nodes = []
                        for n in Elements[ele]:
                            nodes.append(nodecounts[n])

                        str_elecommand = propcommand(ele + eleTag, nodes, eleProps)
                        str_command = "ops." + str_elecommand

                        file_elements.write(str_command + '\n')

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)
                        elements_[ele + eleTag] = nodes
                        lineuniloads[ele + eleTag] = component.Uniload

                elif isinstance(component, Triangle) or isinstance(component, Quad) or isinstance(component, Polygon):

                    for ele in Elements.keys():
                        nodes = []
                        for n in Elements[ele]:
                            nodes.append(nodecounts[n])

                        str_elecommand = propcommand(ele + eleTag, nodes, eleProps)
                        str_command = "ops." + str_elecommand

                        file_elements.write(str_command + '\n')

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)
                        elements_[ele + eleTag] = nodes
                        quaduniloads[ele + eleTag] = component.Uniload

                elif isinstance(component, Brick):
                    for ele in Elements.keys():
                        nodes = []
                        for n in Elements[ele]:
                            nodes.append(nodecounts[n])

                        str_elecommand = propcommand(ele + eleTag, nodes, eleProps)
                        str_command = "ops." + str_elecommand

                        file_elements.write(str_command + '\n')

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)
                        elements_[ele + eleTag] = nodes

                # print("# Elements for component " + component.Name + '  were created.')

                output[component.Name] = [nodes_, elements_, Nodesatsameloc]

            part.LineUniLoads = lineuniloads
            part.QuadUniLoads = quaduniloads
            part.BodyLoads = bodyloads



            for const in part.EqualDofs:
                self.__assignequaldof(part, const, print_command)

            for const in part.RigidDiaphragms:
                self.__assignrigiddiaph(part, const, print_command)

            for const in part.RigidLinks:
                self.__assignrigidlink(part, const, print_command)

            self.__assignspconstraint(part, print_command)

        for part in models_notattached:
            file_elements.write('# Part: ' + part.Name + '\n')
            print('# Part: ', part.Name)
            mrgpartslist = self.MergedParts
            nodes_model = []
            for mrgparts in mrgpartslist:
                merged = False
                mrgnodes = []
                for im in range(len(mrgparts)):
                    if mrgparts[im].Name == part.Name:
                        # print('main ', mrgparts[im].Name)
                        merged = True
                    else:
                        # print('other ', mrgparts[im].Name)
                        for no, co in mrgparts[im].getNodes().items():
                            mrgnodes.append([no, co[0], co[1], co[2]])
                if merged:
                    for mm in mrgnodes:
                        nodes_model.append(mm)

            lineuniloads = {}
            quaduniloads = {}
            bodyloads = {}

            for component in part.Components:
                if len(ops.getNodeTags()) == 0:
                    nodeTag = 0
                else:
                    nodeTag = int(np.max(ops.getNodeTags()))

                if isinstance(component, Point):
                    exnodeTag = False
                    x, y, z = component.XYZ
                    if len(nodes_model) != 0:
                        exnodeTag = self.__nodeexist([x, y, z], nodes_model)


                    if exnodeTag is False:
                        if _ndm == 2:
                            str_command = "ops.node(" + str(int(1 + nodeTag)) + ", " + str(x) + ", " + str(y) + ")"

                        elif _ndm == 3:
                            str_command = "ops.node(" + str(int(1 + nodeTag)) + ", " + str(x) + ", " + str(y) + \
                                          ", " + str(z) + ")"

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)
                        component.NodeTag = 1 + nodeTag
                        nodes_model.append([1 + nodeTag, x, y, z])
                        component.Nodes = {1 + nodeTag: [x, y, z]}
                        if len(component.Rest) != 0:
                            self.__assignrest(1 + nodeTag, component.Rest, print_command)

                        if len(component.Mass) != 0:
                            cmass = component.Mass
                            for i in range(len(cmass)):
                                part.assign_nodalmass([x, y, z], cmass[i], i + 1, 'a')

                        file_nodes = open(_name + "\\" + "file_nodes.txt", "a")
                        file_nodes.write(str_command + '\n')
                        file_nodes.close()
                    else:
                        component.NodeTag = exnodeTag

            for component in part.Components:
                if isinstance(component, Point):
                    continue

                Nodesatsameloc = []
                exnodes = []
                if len(ops.getNodeTags()) == 0:
                    nodeTag = 0
                else:
                    nodeTag = int(np.max(ops.getNodeTags()))

                if len(ops.getEleTags()) == 0:
                    eleTag = 0
                else:
                    eleTag = int(np.max(ops.getEleTags()))

                Nodes, Elements, Noderange = component.createelements()
                eleProps = component.EleProps
                nodes_ = component.Nodes
                elements_ = component.Elements
                nodecounts = {}
                exnodeTag = False
                for tag in Nodes.keys():
                    x = Nodes[tag][0]
                    y = Nodes[tag][1]
                    z = Nodes[tag][2]
                    if len(nodes_model) != 0:
                        exnodeTag = self.__nodeexist([x, y, z], nodes_model)

                    if exnodeTag is False:
                        nodecounts[tag] = tag + nodeTag
                        nodes_[tag + nodeTag] = [x, y, z]
                        nodes_model.append([tag + nodeTag, x, y, z])
                    else:
                        exnodes.append(exnodeTag)
                        nodecounts[tag] = exnodeTag
                        nodes_[exnodeTag] = [x, y, z]

                # Create Node Objects
                file_nodes = open(_name + "\\" + "file_nodes.txt", "a")
                for nod in nodes_.keys():
                    x, y, z = nodes_[nod]
                    if nod not in exnodes:
                        if _ndm == 2:
                            str_command = "ops.node(" + str(int(nod)) + ", " + str(x) + ", " + str(y) + ")"
                        elif _ndm == 3:
                            str_command = "ops.node(" + str(int(nod)) + ", " + str(x) + ", " + str(y) + ", " + str(
                                z) + ")"

                        file_nodes.write(str_command + '\n')

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)

                file_nodes.close()
                nodeset = component.NodeSets

                if isinstance(component, Brick):
                    for face in Noderange.keys():
                        fnodes = Noderange[face]['Nodes']
                        nfnodes = []
                        for nn in fnodes:
                            nfnodes_ = []
                            for n in nn:
                                nfnodes_.append(int(nodecounts[n]))

                            nfnodes.append(nfnodes_)

                        nodeset[face]['Nodes'] = nfnodes

                        fnodes = Noderange[face]['ij']
                        nfnodes_ = []
                        for nn in fnodes:
                            nfnodes_.append(int(nodecounts[nn]))

                        nodeset[face]['ij'] = nfnodes_

                        fnodes = Noderange[face]['jk']
                        nfnodes_ = []
                        for nn in fnodes:
                            nfnodes_.append(int(nodecounts[nn]))

                        nodeset[face]['jk'] = nfnodes_

                        fnodes = Noderange[face]['kl']
                        nfnodes_ = []
                        for nn in fnodes:
                            nfnodes_.append(int(nodecounts[nn]))

                        nodeset[face]['kl'] = nfnodes_

                        fnodes = Noderange[face]['li']
                        nfnodes_ = []
                        for nn in fnodes:
                            nfnodes_.append(int(nodecounts[nn]))

                        nodeset[face]['li'] = nfnodes_


                elif isinstance(component, Quad):

                    nodeset['ij'] = [nodecounts[x] for x in Noderange[0]]
                    nodeset['jk'] = [nodecounts[x] for x in Noderange[1]]
                    nodeset['kl'] = [nodecounts[x] for x in Noderange[2]]
                    nodeset['li'] = [nodecounts[x] for x in Noderange[3]]

                elif isinstance(component, Triangle):

                    nodeset['ij'] = [nodecounts[x] for x in Noderange[0]]
                    nodeset['jk'] = [nodecounts[x] for x in Noderange[1]]
                    nodeset['ki'] = [nodecounts[x] for x in Noderange[2]]
                elif isinstance(component, Polygon):
                    nrcount = 1
                    for node_r in Noderange:
                        nodeset[str(nrcount)] = [nodecounts[x] for x in node_r]
                        nrcount += 1
                elif isinstance(component, Line):
                    nodeset['i'] = nodecounts[Noderange[0]]
                    nodeset['j'] = nodecounts[Noderange[1]]

                if isinstance(component, Line):
                    for ele in Elements.keys():
                        nodes = []
                        for n in Elements[ele]:
                            nodes.append(nodecounts[n])

                        str_elecommand = propcommand(ele + eleTag, nodes, eleProps)
                        str_command = "ops." + str_elecommand

                        file_elements.write(str_command + '\n')

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)
                        elements_[ele + eleTag] = nodes
                        lineuniloads[ele + eleTag] = component.Uniload

                elif isinstance(component, Triangle) or isinstance(component, Quad) or isinstance(component, Polygon):

                    for ele in Elements.keys():
                        nodes = []
                        for n in Elements[ele]:
                            nodes.append(nodecounts[n])

                        str_elecommand = propcommand(ele + eleTag, nodes, eleProps)
                        str_command = "ops." + str_elecommand

                        file_elements.write(str_command + '\n')

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)
                        elements_[ele + eleTag] = nodes
                        quaduniloads[ele + eleTag] = component.Uniload

                elif isinstance(component, Brick):
                    for ele in Elements.keys():
                        nodes = []
                        for n in Elements[ele]:
                            nodes.append(nodecounts[n])

                        str_elecommand = propcommand(ele + eleTag, nodes, eleProps)
                        str_command = "ops." + str_elecommand

                        file_elements.write(str_command + '\n')

                        if print_command.lower() in ['y', 'yes']:
                            print(str_command)

                        eval(str_command)
                        elements_[ele + eleTag] = nodes

                # print("# Elements for component " + component.Name + '  were created.')

                output[component.Name] = [nodes_, elements_, Nodesatsameloc]

            part.LineUniLoads = lineuniloads
            part.QuadUniLoads = quaduniloads
            part.BodyLoads = bodyloads



            for const in part.EqualDofs:
                self.__assignequaldof(part, const, print_command)

            for const in part.RigidDiaphragms:
                self.__assignrigiddiaph(part, const, print_command)

            for const in part.RigidLinks:
                self.__assignrigidlink(part, const, print_command)

            self.__assignspconstraint(part, print_command)

        for const in self.EqualDofs:
            self.__assignequaldof_model(const, print_command)

        for const in self.RigidDiaphragms:
            self.__assignrigiddiaph_model(const, print_command)

        for const in self.RigidLinks:
            self.__assignrigidlink_model(const, print_command)

        self.__assignspconstraint_model(print_command)

        file_elements.close()

        file_model = self.Name + "\\" + "file_model.pkl"
        fmodel = open(file_model, 'wb')
        dill.dump(self, fmodel)
        fmodel.close()

        print('# Model: ', self.Name, ' was created.')

        return output

    def __separate_points(self, parts):
        _points = []
        _others = []
        for part in parts:
            for com in part.Components:
                if isinstance(com, Point):
                    _points.append(com)
                else:
                    _others.append(com)

        return _others, _points

 # End of Model Class
class geomTransf:
    def __init__(self, name='', type='Linear', vecxz=[], jntOffset_I=[], jntOffset_J=[]):
        self.Name = name
        self.Type = type
        self.Tag = 1
        self.Vecxz = vecxz
        self.JntOffset_I = jntOffset_I
        self.JntOffset_J = jntOffset_J

    def __get_Tag(self):
        return self._Tag

    def __set_Tag(self, val):
        if (type(val) != int):
            raise ValueError("Tag must be positive integer value")

        if (val <= 0):
            raise ValueError("Tag must be positive integer value")

        self._Tag = val

    def __del_Tag(self):
        del self._Tag

    Tag = property(__get_Tag, __set_Tag, __del_Tag)


    def create_command(self):
        type = self.Type
        tag = self.Tag
        vecxz = self.Vecxz
        jntOffset_I = self.JntOffset_I
        jntOffset_J = self.JntOffset_J
        str_v = ''
        if len(vecxz) != 0:
            str_v = ', ' + str(vecxz[0]) + ', ' + str(vecxz[1]) + ', ' + str(vecxz[2])

        str_offset = ''
        if len(jntOffset_I) != 0 or len(jntOffset_J) != 0:
            str_offset = ', \'-jntOffset\', '

        if len(jntOffset_I) != 0:
            str_offset = str_offset + str(jntOffset_I[0]) + ', ' + str(jntOffset_I[1]) + ', ' + str(jntOffset_I[2])

        if len(jntOffset_J) != 0:
            str_offset = str_offset + ', ' + str(jntOffset_J[0]) + ', ' + str(jntOffset_J[1]) + ', ' + str(jntOffset_J[2])

        str_com = 'ops.geomTransf(' + '\'' + type + '\', ' + str(tag) + str_v + str_offset + ')'

        return str_com


class Part:
    def __init__(self, name='', attach='y'):
        self.Tag = 1
        self.Name = name
        self.Attach = attach
        self.Components = []
        self.NodalLoads = []
        self.LineUniLoads = []
        self.QuadUniLoads = []
        self.BodyLoads = []
        self.SurfLoads = []
        self.NodalMasses = []
        self.SpConstraints = []
        self.EqualDofs = []
        self.RigidDiaphragms = []
        self.RigidLinks = []

    def __get_Tag(self):
        return self._Tag

    def __set_Tag(self, val):
        if (type(val) != int):
            raise ValueError("Tag must be positive integer value")

        if (val <= 0):
            raise ValueError("Tag must be positive integer value")

        self._Tag = val

    def __del_Tag(self):
        del self._Tag

    Tag = property(__get_Tag, __set_Tag, __del_Tag)

    def add_component(self, *components):
        # comps = self.Components
        for co in components:
            if isinstance(co, list):
                for cc in co:
                    self.Components.append(cc)
            else:
                self.Components.append(co)


    def remove_component(self, component):
        components = self.Components
        components.remove(component)

    def assign_nodalload(self, pattern, xyz, value, direction=2, option='add'):
        global _ndf
        global _tolerance
        dofvals = list(np.arange(1, _ndf + 1, dtype=int))
        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in dofvals:
            raise ValueError('direction must be 1 through ndf')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        uniloads = self.NodalLoads
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                df_xyz = True in (abs((np.array(load[1]) - np.array(xyz))) > _tolerance)
                if df_xyz is False:
                    if (load[0]['Name'] != pattern['Name']):
                        newuniloads.append(load)

            self.NodalLoads = newuniloads
            return

        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                df_xyz = True in (abs((np.array(load[1]) - np.array(xyz))) > _tolerance)
                if df_xyz is False:
                    if load[0]['Name'] != pattern['Name']:
                        newuniloads.append(load)

            newuniloads.append([pattern, xyz, value, direction])
            self.NodalLoads = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            df_xyz = True in (abs((np.array(load[1]) - np.array(xyz))) > _tolerance)
            if df_xyz is False:
                if load[0]['Name'] == pattern['Name'] and load[2] == direction:
                    if option.lower() in ['add', 'a']:
                        uniloads[i][1] += value
                        return

        uniloads.append([pattern, xyz, value, direction])

    def find_node(self, xyz):
        global _ndm
        global _tolerance
        nodes = self.getNodes()
        if _ndm == 3:
            x, y, z = xyz
        elif _ndm == 2:
            x, y = xyz[0], xyz[1]
            z = 0

        nodeTags = []
        for nod, coords in nodes.items():
            if _ndm == 3:
                xn, yn, zn = coords
            elif _ndm == 2:
                xn, yn = coords
                zn = 0

            if (abs(x - xn) + abs(y - yn) + abs(z - zn)) < _tolerance:
                nodeTags.append(nod)
        if len(nodeTags) == 0:
            return False
        elif len(nodeTags) == 1:
            return nodeTags[0]
        else:
            return nodeTags

    def assign_nodalmass(self, xyz, value, direction=2, option='add'):
        global _ndf
        global _tolerance
        dofvals = list(np.arange(1, _ndf + 1, dtype=int))
        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in dofvals:
            raise ValueError('direction must be 1 through ndf')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        uniloads = self.NodalMasses
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                df_xyz = True in (abs((np.array(load[0]) - np.array(xyz))) > _tolerance)
                if df_xyz is False:
                        newuniloads.append(load)

            self.NodalMasses = newuniloads
            return

        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                df_xyz = True in (abs((np.array(load[0]) - np.array(xyz))) > _tolerance)
                if df_xyz is False:
                        newuniloads.append(load)

            newuniloads.append([xyz, value, direction])
            self.NodalMasses = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            df_xyz = True in (abs((np.array(load[0]) - np.array(xyz))) > _tolerance)
            if df_xyz is False:
                if load[2] == direction:
                    if option.lower() in ['add', 'a']:
                        uniloads[i][1] += value
                        return

        uniloads.append([xyz, value, direction])

    def assign_spconstraint(self, xlim=[], ylim=[], zlim=[], dofs=[]):
        global _ndf
        dofs = list(dict.fromkeys(dofs))
        dirvals = list(np.arange(1, _ndf+1, dtype=int))

        if len(dofs) != 0:
            for dir in dofs:
                if dir not in dirvals:
                    err = 'direction must be an integer value between 1 through ndf = ' + str(_ndf)
                    raise ValueError(err)

        spconsts = self.SpConstraints
        spconsts.append([xlim, ylim, zlim, dofs])

    def assign_equaldof(self, xyzr, xclim=[], yclim=[], zclim=[], dofs=[]):
        global _ndf
        dofs = list(dict.fromkeys(dofs))
        dirvals = list(np.arange(1, _ndf + 1, dtype=int))
        if len(dofs) != 0:
            for dir in dofs:
                if dir not in dirvals:
                    raise ValueError('dof must be a integer between 1 through ndf = ' + str(_ndf))

        eqdofs = self.EqualDofs
        eqdofs.append([xyzr, xclim, yclim, zclim, dofs])

    def assign_rigiddiaphragm(self, xyzr, perpdirn=2, xclim=[], yclim=[], zclim=[], massr=[], rests=[2, 4, 6]):
        rgdiaphs = self.RigidDiaphragms

        rgdiaphs.append([xyzr, perpdirn, xclim, yclim, zclim, massr, rests])

    def assign_rigidlink(self, xyzr, type='beam', xclim=[], yclim=[], zclim=[]):
        rglinks = self.RigidLinks
        rglinks.append([xyzr, type, xclim, yclim, zclim])

    def getNodes(self):
        model_nodes = {}
        for m in self.Components:
            model_nodes.update(m.Nodes)

        return model_nodes

    def getElements(self):
        model_elements = {}
        for m in self.Components:
            if not isinstance(m, Point):
                model_elements.update(m.Elements)

        return model_elements

def replicate_linear(part, number, dx, dy, dz, otherpart=None):
    allnewcomponents = []
    for m in part.Components:
        newcomponents = m.replicate_linear(number, dx, dy, dz)
        if number == 1:
            allnewcomponents.append(newcomponents)
        else:
            allnewcomponents.extend(newcomponents)

    if otherpart == None:
        for newm in allnewcomponents:
            part.add_component(newm)
    elif isinstance(otherpart, Part):
        for newm in allnewcomponents:
                otherpart.add_component(newm)

def replicate_mirror(part, xyz1, xyz2, xyz3, otherpart=None):
    allnewcomponents=[]
    for m in part.Components:
        newcomponents = m.replicate_mirror(xyz1, xyz2, xyz3)
        allnewcomponents.append(newcomponents)

    if otherpart == None:
        for newm in allnewcomponents:
            part.add_component(newm)

    elif isinstance(otherpart, Part):
        for newm in allnewcomponents:
                otherpart.add_component(newm)

def replicate_rotate(part, number, xyz1, xyz2, teta, otherpart=None):
    allnewcomponents=[]
    for m in part.Components:
        newcomponents = m.replicate_rotate(number, xyz1, xyz2, teta)
        if number == 1:
            allnewcomponents.append(newcomponents)
        else:
            allnewcomponents.extend(newcomponents)

    if otherpart == None:
        for newm in allnewcomponents:
            part.add_component(newm)

    elif isinstance(otherpart, Part):
        for newm in allnewcomponents:
                otherpart.add_component(newm)

def merge_parts(mainpart, *parts):
    for part in parts:
        for m in part.Components:
            mainpart.add_component(m)

def plot_parts(*parts, ax, name='n', propname='y', subdivisions='y', localcoord='n', linewidth=0.2, pointsize=0.2,
               edgelinewidth=0.2, fill='y',
               coloring='eleProps', legend='y', fontsize=3, xlim=[], ylim=[], zlim=[], facenumber='n',alpha=0.5):
    eleprops = {}
    for part in parts:
        for component in part.Components:
            if not isinstance(component, Point):
                ename = component.EleProps['Name']
                co = component.EleProps['Color']
                eleprops[ename] = co
            plot_component(ax, component, name, propname, subdivisions, localcoord, linewidth, pointsize, edgelinewidth, fill, coloring,
                   fontsize, xlim, ylim, zlim, facenumber, alpha)


    # Creating legend with color box
    if (coloring == 'eleProps') and (legend.lower() in ['y', 'yes']):
        pop = []
        for key, val in eleprops.items():
            pop.append(mpatches.Patch(color=val, label=key))
        ax.legend(handles=pop, fontsize=fontsize)

class Brick:
    def __init__(self, name, eleProps, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, N12=5, N14=5, N15=5):
        self.Name = name
        self.EleProps = eleProps
        self.XYZ1 = xyz1
        self.XYZ2 = xyz2
        self.XYZ3 = xyz3
        self.XYZ4 = xyz4
        self.XYZ5 = xyz5
        self.XYZ6 = xyz6
        self.XYZ7 = xyz7
        self.XYZ8 = xyz8
        self.N12 = N12
        self.N14 = N14
        self.N15 = N15
        self.Surfload = []
        self.Bodyload = []
        self.NodeSets = {1: {'Nodes': [],
                          'ij': [],
                          'jk': [],
                          'kl': [],
                          'li': []
                          },
                          2: {'Nodes': [],
                          'ij': [],
                          'jk': [],
                          'kl': [],
                          'li': []
                          },
                          3: {'Nodes': [],
                          'ij': [],
                          'jk': [],
                          'kl': [],
                          'li': []
                          },
                          4: {'Nodes': [],
                          'ij': [],
                          'jk': [],
                          'kl': [],
                          'li': []
                          },
                          5: {'Nodes': [],
                          'ij': [],
                          'jk': [],
                          'kl': [],
                          'li': []
                          },
                          6: {'Nodes': [],
                          'ij': [],
                          'jk': [],
                          'kl': [],
                          'li': []
                          }
               }
        self.Nodes = {}
        self.Elements = {}
    ###### validation VBlock ( Set and Get Properties ) ########################
    def __get_name(self):
            return self._Name

    def __set_name(self, name):

        if type(name) is not str:
            raise ValueError("name must be string")
        self._Name = name

    def __del_name(self):
        del self._Name

    Name = property(__get_name, __set_name, __del_name)

    # XYZ1
    def __get_XYZ1(self):
        return self._XYZ1

    def __set_XYZ1(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")

        self._XYZ1 = value

    def __del_XYZ1(self):
        del self._XYZ1

    XYZ1 = property(__get_XYZ1, __set_XYZ1, __del_XYZ1)

    # XYZ2
    def __get_XYZ2(self):
        return self._XYZ2

    def __set_XYZ2(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")

        self._XYZ2 = value

    def __del_XYZ2(self):
        del self._XYZ2

    XYZ2 = property(__get_XYZ2, __set_XYZ2, __del_XYZ2)

    # XYZ3
    def __get_XYZ3(self):
        return self._XYZ3

    def __set_XYZ3(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")

        self._XYZ3 = value

    def __del_XYZ3(self):
        del self._XYZ3

    XYZ3 = property(__get_XYZ3, __set_XYZ3, __del_XYZ3)

    # XYZ4
    def __get_XYZ4(self):
        return self._XYZ4

    def __set_XYZ4(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")

        self._XYZ4 = value

    def __del_XYZ4(self):
        del self._XYZ4

    XYZ4 = property(__get_XYZ4, __set_XYZ4, __del_XYZ4)

    # XYZ5
    def __get_XYZ5(self):
        return self._XYZ5

    def __set_XYZ5(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")

        self._XYZ5 = value

    def __del_XYZ5(self):
        del self._XYZ5

    XYZ5 = property(__get_XYZ5, __set_XYZ5, __del_XYZ5)

    # XYZ6
    def __get_XYZ6(self):
        return self._XYZ6

    def __set_XYZ6(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")

        self._XYZ6 = value

    def __del_XYZ6(self):
        del self._XYZ6

    XYZ6 = property(__get_XYZ6, __set_XYZ6, __del_XYZ6)

    # XYZ7
    def __get_XYZ7(self):
        return self._XYZ7

    def __set_XYZ7(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")

        self._XYZ7 = value

    def __del_XYZ7(self):
        del self._XYZ7

    XYZ7 = property(__get_XYZ7, __set_XYZ7, __del_XYZ7)

    # XYZ8
    def __get_XYZ8(self):
        return self._XYZ8

    def __set_XYZ8(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")

        self._XYZ8 = value

    def __del_XYZ8(self):
        del self._XYZ8

    XYZ8 = property(__get_XYZ8, __set_XYZ8, __del_XYZ8)

    # N12 Validation
    def __get_N12(self):
        return self._N12

    def __set_N12(self, val):
        if (type(val) != int):
            raise ValueError("Number of subdivisions must be positive integer value")

        if (val <= 0):
            raise ValueError("Number of subdivisions must be positive integer value")

        self._N12 = val

    def __del_N12(self):
        del self._N12

    N12 = property(__get_N12, __set_N12, __del_N12)

    # N14 Validation
    def __get_N14(self):
        return self._N14

    def __set_N14(self, val):
        if (type(val) != int):
            raise ValueError("Number of subdivisions must be positive integer value")

        if (val <= 0):
            raise ValueError("Number of subdivisions must be positive integer value")

        self._N14 = val

    def __del_N14(self):
        del self._N14

    N14 = property(__get_N14, __set_N14, __del_N14)

    # N15 Validation
    def __get_N15(self):
        return self._N15

    def __set_N15(self, val):
        if (type(val) != int):
            raise ValueError("Number of subdivisions must be positive integer value")

        if (val <= 0):
            raise ValueError("Number of subdivisions must be positive integer value")

        self._N15 = val

    def __del_N15(self):
        del self._N15

    N15 = property(__get_N15, __set_N15, __del_N15)

    # EleProps Validation
    def __get_EleProps(self):
        return self._EleProps

    def __set_EleProps(self, value):
        if type(value) != dict:
            raise ValueError('eleProps must be a python dictionary')

        self._EleProps = value

    def __del_EleProps(self):
        del self._EleProps

    EleProps = property(__get_EleProps, __set_EleProps, __del_EleProps)

    ## End of validation

    ###### loading ########################
    def assign_surfload(self, pattern, faces, value, direction=3, coord='local', option='add'):
        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in [1, 2, 3]:
            raise ValueError('direction must be one of 1, 2 or 3')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        if isinstance(faces, list):
            for face in faces:
                if face not in [1, 2, 3, 4, 5, 6]:
                    raise ValueError('face must be one of 1, 2, 3, 4, 5 or 6')

            if len(faces) == 0:
                faces = [1, 2, 3, 4, 5, 6]

        else:
            if faces not in [1, 2, 3, 4, 5, 6]:
                raise ValueError('face must be one of 1, 2, 3, 4, 5 or 6')
            faces = [faces]

        uniloads = self.Surfload
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)
                    continue
                if load[1] in faces:
                    continue
                else:
                    newuniloads.append(load)

            self.Surfload = newuniloads
            return

        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)
                    continue
                if load[1] in faces:
                    continue
                else:
                    newuniloads.append(load)

            for face in faces:
                newuniloads.append([pattern, face, value, direction, coord])

            self.Surfload = newuniloads
            return

        for face in faces:
            newload = True
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] == pattern['Name'] and load[1] == face and load[3] == direction and load[4] == coord:
                    uniloads[i][2] += value
                    newload = False

            if newload:
                uniloads.append([pattern, face, value, direction, coord])

    def assign_bodyload(self, pattern, value, direction=2, option='add'):
        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in [1, 2, 3]:
            raise ValueError('direction must be one of 1, 2 or 3')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        uniloads = self.Bodyload
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            self.Bodyload = newuniloads
            return

        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            newuniloads.append([pattern, value, direction])
            self.Bodyload = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            if load[0]['Name'] == pattern['Name'] and load[2] == direction:
                if option.lower() in ['add', 'a']:
                    uniloads[i][1] += value
                    return

        uniloads.append([pattern, value, direction])

    def __copy(self):
        newcomp = Brick(self.Name, self.EleProps, self.XYZ1, self.XYZ2, self.XYZ3, self.XYZ4, self.XYZ5, self.XYZ6,
                        self.XYZ7, self.XYZ8, N12=self.N12, N14=self.N14, N15=self.N15)
        newcomp.Surfload= copy.deepcopy(self.Surfload)
        newcomp.Bodyload = copy.deepcopy(self.Bodyload)

        return newcomp

    ###### linear replicate ########################
    def replicate_linear(self, number, dx, dy, dz):
        if type(number) != int:
            raise ValueError("Number of replications must be positive integer value")

        if number <= 0:
            raise ValueError("Number of replications must be positive integer value")

        if isinstance(dx, numbers.Number) is False:
            raise ValueError('dx must be a numeric value')

        if isinstance(dy, numbers.Number) is False:
            raise ValueError('dy must be a numeric value')

        if isinstance(dz, numbers.Number) is False:
            raise ValueError('dz must be a numeric value')

        newcomponents = []
        name = self.Name
        x1, y1, z1 = self.XYZ1
        x2, y2, z2 = self.XYZ2
        x3, y3, z3 = self.XYZ3
        x4, y4, z4 = self.XYZ4
        x5, y5, z5 = self.XYZ5
        x6, y6, z6 = self.XYZ6
        x7, y7, z7 = self.XYZ7
        x8, y8, z8 = self.XYZ8
        for i in range(number):
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newx1, newy1, newz1 = x1 + (i + 1) * dx, y1 + (i + 1) * dy, z1 + (i + 1) * dz
            newx2, newy2, newz2 = x2 + (i + 1) * dx, y2 + (i + 1) * dy, z2 + (i + 1) * dz
            newx3, newy3, newz3 = x3 + (i + 1) * dx, y3 + (i + 1) * dy, z3 + (i + 1) * dz
            newx4, newy4, newz4 = x4 + (i + 1) * dx, y4 + (i + 1) * dy, z4 + (i + 1) * dz
            newx5, newy5, newz5 = x5 + (i + 1) * dx, y5 + (i + 1) * dy, z5 + (i + 1) * dz
            newx6, newy6, newz6 = x6 + (i + 1) * dx, y6 + (i + 1) * dy, z6 + (i + 1) * dz
            newx7, newy7, newz7 = x7 + (i + 1) * dx, y7 + (i + 1) * dy, z7 + (i + 1) * dz
            newx8, newy8, newz8 = x8 + (i + 1) * dx, y8 + (i + 1) * dy, z8 + (i + 1) * dz
            newmember.XYZ1 = [newx1, newy1, newz1]
            newmember.XYZ2 = [newx2, newy2, newz2]
            newmember.XYZ3 = [newx3, newy3, newz3]
            newmember.XYZ4 = [newx4, newy4, newz4]
            newmember.XYZ5 = [newx5, newy5, newz5]
            newmember.XYZ6 = [newx6, newy6, newz6]
            newmember.XYZ7 = [newx7, newy7, newz7]
            newmember.XYZ8 = [newx8, newy8, newz8]

            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### replicate mirror ########################
    def replicate_mirror(self, xyz1, xyz2, xyz3):
        name = self.Name
        newname = name + "_mir"
        newmember = self.__copy()
        newmember.XYZ1 = MyMath.mirrorpoint(self.XYZ1, xyz1, xyz2, xyz3)
        newmember.XYZ2 = MyMath.mirrorpoint(self.XYZ2, xyz1, xyz2, xyz3)
        newmember.XYZ3 = MyMath.mirrorpoint(self.XYZ3, xyz1, xyz2, xyz3)
        newmember.XYZ4 = MyMath.mirrorpoint(self.XYZ4, xyz1, xyz2, xyz3)
        newmember.XYZ5 = MyMath.mirrorpoint(self.XYZ5, xyz1, xyz2, xyz3)
        newmember.XYZ6 = MyMath.mirrorpoint(self.XYZ6, xyz1, xyz2, xyz3)
        newmember.XYZ7 = MyMath.mirrorpoint(self.XYZ7, xyz1, xyz2, xyz3)
        newmember.XYZ8 = MyMath.mirrorpoint(self.XYZ8, xyz1, xyz2, xyz3)
        newmember.Name = newname
        return newmember

    ###### replicate rotate ########################
    def replicate_rotate(self, number, xyz1, xyz2, teta):
        newcomponents = []
        name = self.Name
        for i in range(number):
            rot_t = teta * (i + 1)
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newmember.XYZ1 = MyMath.rotatepoint(self.XYZ1, xyz1, xyz2, rot_t)
            newmember.XYZ2 = MyMath.rotatepoint(self.XYZ2, xyz1, xyz2, rot_t)
            newmember.XYZ3 = MyMath.rotatepoint(self.XYZ3, xyz1, xyz2, rot_t)
            newmember.XYZ4 = MyMath.rotatepoint(self.XYZ4, xyz1, xyz2, rot_t)
            newmember.XYZ5 = MyMath.rotatepoint(self.XYZ5, xyz1, xyz2, rot_t)
            newmember.XYZ6 = MyMath.rotatepoint(self.XYZ6, xyz1, xyz2, rot_t)
            newmember.XYZ7 = MyMath.rotatepoint(self.XYZ7, xyz1, xyz2, rot_t)
            newmember.XYZ8 = MyMath.rotatepoint(self.XYZ8, xyz1, xyz2, rot_t)
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### Create Elements ########################

    def createelements(self):
        global _ndf
        global _ndm
        eleProps = self.EleProps
        xyz1 = self.XYZ1
        xyz2 = self.XYZ2
        xyz3 = self.XYZ3
        xyz4 = self.XYZ4
        xyz5 = self.XYZ5
        xyz6 = self.XYZ6
        xyz7 = self.XYZ7
        xyz8 = self.XYZ8
        N12 = self.N12
        N14 = self.N14
        N15 = self.N15

        xyz = [xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8]

        if _ndm == 3:
            for xyzi in xyz:
                if len(xyzi) != 3:
                    raise ValueError("ndm = 3: xyz should be a list contains coordinates [x, y, z]")
        elif _ndm == 2:
            for xyzi in xyz:
                if len(xyzi) < 2:
                    raise ValueError("ndm = 2: xyz should be a list contains coordinates [x, y]")

            xyz1 = [xyz1[0], xyz1[1], 0]
            xyz2 = [xyz2[0], xyz2[1], 0]
            xyz3 = [xyz3[0], xyz3[1], 0]
            xyz4 = [xyz4[0], xyz4[1], 0]
            xyz5 = [xyz5[0], xyz5[1], 0]
            xyz6 = [xyz6[0], xyz6[1], 0]
            xyz7 = [xyz7[0], xyz7[1], 0]
            xyz8 = [xyz8[0], xyz8[1], 0]

        coords, Noderange, Nodes = MyMath.dividecube(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, N12, N14, N15)

        edgeNodes = MyMath.extractbricknodesets(Noderange)
        Elements = MyMath.extractbrickelements(coords, N12, N14)

        return Nodes, Elements, edgeNodes

class Polygon:
    def __init__(self, name, eleProps, xyz, Ndiv=4):
        self.Name = name
        self.EleProps = eleProps
        self.XYZ = xyz
        self.NDiv = Ndiv
        self.Uniload = []
        self.NodeSets = {}
        self.Nodes = {}
        self.Elements = {}
    ###### validation VBlock ( Set and Get Properties ) ########################
    def __get_name(self):
            return self._Name

    def __set_name(self, name):
        if type(name) is not str:
            raise ValueError("name must be string")
        self._Name = name

    def __del_name(self):
        del self._Name

    Name = property(__get_name, __set_name, __del_name)

    # XYZ
    def __get_XYZ(self):
        return self._XYZ

    def __set_XYZ(self, value):
        value = list(value)
        for i in range(len(value)):
            _xyz = value[i]
            if isinstance(_xyz, Point):
                _xyz = _xyz.XYZ
            if len(_xyz) not in [2, 3]:
                raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

            for i in range(len(_xyz)):
                if type(_xyz[i]) is int:
                    _xyz[i] = float(_xyz[i])

                if isinstance(_xyz[i], numbers.Number) is False:
                    raise ValueError("Coordinates must be numeric values")
            if len(_xyz) == 2:
                _xyz.append(0.0)
            value[i] = _xyz

        self._XYZ = value

    def __del_XYZ(self):
        del self._XYZ

    XYZ = property(__get_XYZ, __set_XYZ, __del_XYZ)


    # NDiv Validation
    def __get_NDiv(self):
        return self._NDiv

    def __set_NDiv(self, val):
        if (type(val) != int):
            raise ValueError("Number of subdivisions must be positive integer value")

        if (val <= 0):
            raise ValueError("Number of subdivisions must be positive integer value")

        self._NDiv = val

    def __del_NDiv(self):
        del self._NDiv

    NDiv = property(__get_NDiv, __set_NDiv, __del_NDiv)

    # EleProps Validation
    def __get_EleProps(self):
        return self._EleProps

    def __set_EleProps(self, value):
        if type(value) != dict:
            raise ValueError('eleProps must be a python dictionary')

        self._EleProps = value

    def __del_EleProps(self):
        del self._EleProps

    EleProps = property(__get_EleProps, __set_EleProps, __del_EleProps)

    ## End of validation

    ###### loading ########################
    def assign_uniload(self, pattern, value, direction=3, coord='local', option='add'):

        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in [1, 2, 3]:
            raise ValueError('direction must be one of 1, 2 or 3')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        if coord.lower() not in ['global', 'g', 'local', 'l']:
            raise ValueError("coord must be \'global\', \'g\' or \'local\', \'l\'")

        uniloads = self.Uniload
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            self.Uniload = newuniloads
            return

        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            newuniloads.append([pattern, value, direction, coord])
            self.Uniload = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            if load[0]['Name'] == pattern['Name'] and load[2] == direction and load[3] == coord:
                if option.lower() in ['add', 'a']:
                    uniloads[i][1] += value
                    return

        uniloads.append([pattern, value, direction, coord])

    def __copy(self):
        newcomp = Polygon(self.Name, self.EleProps, self.XYZ, Ndiv=self.NDiv)
        newcomp.Uniload = copy.deepcopy(self.Uniload)

        return newcomp

    ###### linear replicate ########################
    def replicate_linear(self, number, dx, dy, dz):
        if (type(number) != int):
            raise ValueError("Number of replications must be positive integer value")

        if (number <= 0):
            raise ValueError("Number of replications must be positive integer value")

        if isinstance(dx, numbers.Number) is False :
            raise ValueError('dx must be a numeric value')

        if isinstance(dy, numbers.Number) is False:
            raise ValueError('dy must be a numeric value')

        if isinstance(dz, numbers.Number) is False:
            raise ValueError('dz must be a numeric value')

        newcomponents = []
        name = self.Name
        xyz = self.XYZ
        for i in range(number):
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            xyznew = []
            for j in range(len(xyz)):
                newxi, newyi, newzi = xyz[j][0] + (i + 1) * dx, xyz[j][1] + (i + 1) * dy, xyz[j][2]  + (i + 1) * dz
                xyznew.append([newxi, newyi, newzi])

            newmember.XYZ = xyznew
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### replicate mirror ########################
    def replicate_mirror(self, xyz1, xyz2, xyz3):
        name = self.Name
        newname = name + "_mir"
        xyz = self.XYZ
        newmember = self.__copy()
        xyznew = []

        for j in range(len(xyz)):
            newxyz = MyMath.mirrorpoint(xyz[j], xyz1, xyz2, xyz3)
            xyznew.append(newxyz)

        newmember.XYZ = xyznew
        newmember.Name = newname
        return newmember

    ###### replicate rotate ########################
    def replicate_rotate(self, number, xyz1, xyz2, teta):
        newcomponents = []
        name = self.Name
        xyz = self.XYZ
        for i in range(number):
            rot_t = teta * (i + 1)
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            xyznew = []
            for j in range(len(xyz)):
                newxyz = MyMath.rotatepoint(xyz[j], xyz1, xyz2, rot_t)
                xyznew.append(newxyz)
            newmember.Name = newname
            newmember.XYZ = xyznew
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    def __createcomponents(self):
        components = []
        xyz = self.XYZ
        if len(xyz) == 1:
            pass
        elif len(xyz) == 2:
            pass
        elif len(xyz) == 3:
            components.append(Triangle(self.Name, self.EleProps, xyz[0], xyz[1], xyz[2], Ndiv=self.NDiv))
        elif len(xyz) == 4:
            components.append(Quad(self.Name,self.EleProps,xyz[0], xyz[1], xyz[2], xyz[3], Nij=self.NDiv,
                                Njk=self.NDiv))
        else:
            node_tags = list(np.linspace(1, len(xyz), len(xyz), dtype=int))

            nodenum = len(node_tags)
            while nodenum > 4:
                a = [node_tags[0]-1, node_tags[1]-1, node_tags[-2]-1, node_tags[-1]-1]
                components.append(Quad(self.Name, self.EleProps, xyz[a[0]], xyz[a[1]], xyz[a[2]], xyz[a[3]], Nij=self.NDiv,
                                    Njk=self.NDiv))
                node_tags.remove(node_tags[0])
                node_tags.remove(node_tags[-1])
                nodenum = len(node_tags)

            if nodenum == 3:
                components.append(Triangle(self.Name, self.EleProps, xyz[node_tags[0]-1], xyz[node_tags[1]-1],
                                        xyz[node_tags[2]-1], Ndiv=self.NDiv))
            elif nodenum == 4:

                components.append(Quad(self.Name, self.EleProps, xyz[node_tags[0]-1], xyz[node_tags[1]-1], xyz[node_tags[2]-1],
                                    xyz[node_tags[3]-1], Nij=self.NDiv, Njk=self.NDiv))

        return components

    def createelements(self):
        n = len(self.XYZ)
        components = self.__createcomponents()
        components2 = []
        Elements = {}
        Nodes = {}
        edgeNodes = []

        if len(components) == 1:
                Nodes, Elements, edgeNodes = components[0].createelements()
        else:
            elecount = 0
            nodecount = 0

            for m in components:
                mnodes, melements, medgenodes = m.createelements()
                mnodes2={}
                melements2 = {}
                medgenodes2 = []
                for el in melements.keys():
                    elenodes = melements[el]
                    nodetags = [x + nodecount for x in elenodes]
                    eletag = el + elecount
                    melements2[eletag] = nodetags

                for no in mnodes.keys():
                    xyz_n = mnodes[no]
                    nodetag = no + nodecount
                    mnodes2[nodetag] = xyz_n

                for i in range(len(medgenodes)):
                    nodetags = [x + nodecount for x in medgenodes[i]]
                    medgenodes2.append(nodetags)

                elecount = max(melements2.keys())
                nodecount = max(mnodes2.keys())

                components2.append([mnodes2, melements2, medgenodes2])

            edgenodes_temp = [[]] * n

            for i in range(len(components2) - 1):
                mnodes_1, melements_1, medgenodes_1 = components2[i]
                edgenodes_temp[i] = medgenodes_1[0]
                edgenodes_temp[n-i-2] = medgenodes_1[2]
                if i == 0:
                    edgenodes_temp[-1] = medgenodes_1[-1]

            mnodes_1, melements_1, medgenodes_1 = components2[-1]
            if len(medgenodes_1) == 4:
                edgenodes_temp[int(n/2 - 2)] = medgenodes_1[0]
                edgenodes_temp[int(n / 2 - 1)] = medgenodes_1[1]
                edgenodes_temp[int(n / 2)] = medgenodes_1[2]

            elif len(medgenodes_1) == 3:
                m = (n+1) / 2
                edgenodes_temp[int(m - 2)] = medgenodes_1[0]
                edgenodes_temp[int(m - 1)] = medgenodes_1[1]


            for i in range(len(components2) - 1):
                mnodes_1, melements_1, medgenodes_1 = components2[i]
                mnodes_2, melements_2, medgenodes_2 = components2[i + 1]
                repnodes_1 = medgenodes_1[1]
                repnodes_2 = medgenodes_2[-1]
                repnodes_2.reverse()

                for ke in list(melements_2.keys()):
                    for j in range(len(repnodes_1)):
                        for k in range(len(melements_2[ke])):
                            if melements_2[ke][k] == repnodes_2[j]:
                                melements_2[ke][k] = repnodes_1[j]

                for nod in repnodes_2:
                    mnodes_2.pop(nod)

                for nod in mnodes_1.keys():
                    Nodes[nod] = mnodes_1[nod]

                for nod in mnodes_2.keys():
                    Nodes[nod] = mnodes_2[nod]

                for j in range(len(repnodes_1)):
                    for l in range(len(edgenodes_temp)):
                        for k in range(len(edgenodes_temp[l])):
                            if edgenodes_temp[l][k] == repnodes_2[j]:
                                edgenodes_temp[l][k] = repnodes_1[j]

                Elements.update(melements_1)
                Elements.update(melements_2)

            edgeNodes = edgenodes_temp

        return Nodes, Elements, edgeNodes

class Quad:
    def __init__(self, name, eleProps, xyzi, xyzj, xyzk, xyzl, meshsize=0.0, Nij=5, Njk=5):
        self.Name = name
        self.EleProps = eleProps
        self.XYZi = xyzi
        self.XYZj = xyzj
        self.XYZk = xyzk
        self.XYZl = xyzl
        self.Nij = Nij
        self.Njk = Njk
        self.Meshsize = meshsize
        self.Uniload = []
        self.NodeSets = {'ij': [],'jk': [],'kl': [],'li': []}
        self.Nodes = {}
        self.Elements = {}
    ###### validation VBlock ( Set and Get Properties ) ########################
    def __get_name(self):
            return self._Name

    def __set_name(self, name):
        if type(name) is not str:
            raise ValueError("name must be string")
        self._Name = name

    def __del_name(self):
        del self._Name

    Name = property(__get_name, __set_name, __del_name)

    # XYZi
    def __get_XYZi(self):
        return self._XYZi

    def __set_XYZi(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)
        self._XYZi = value

    def __del_XYZi(self):
        del self._XYZi

    XYZi = property(__get_XYZi, __set_XYZi, __del_XYZi)

    # XYZj
    def __get_XYZj(self):
        return self._XYZj

    def __set_XYZj(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)
        self._XYZj = value

    def __del_XYZj(self):
        del self._XYZj

    XYZj = property(__get_XYZj, __set_XYZj, __del_XYZj)

    # XYZk
    def __get_XYZk(self):
        return self._XYZk

    def __set_XYZk(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)
        self._XYZk = value

    def __del_XYZk(self):
        del self._XYZk

    XYZk = property(__get_XYZk, __set_XYZk, __del_XYZk)

    # XYZl
    def __get_XYZl(self):
        return self._XYZl

    def __set_XYZl(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)
        self._XYZl = value

    def __del_XYZl(self):
        del self._XYZl

    XYZl = property(__get_XYZl, __set_XYZl, __del_XYZl)


    # Nij Validation
    def __get_Nij(self):
        return self._Nij

    def __set_Nij(self, val):
        if (type(val) != int):
            raise ValueError("Number of subdivisions must be positive integer value")

        if (val <= 0):
            raise ValueError("Number of subdivisions must be positive integer value")

        self._Nij = val

    def __del_Nij(self):
        del self._Nij

    Nij = property(__get_Nij, __set_Nij, __del_Nij)


    # Njk Validation
    def __get_Njk(self):
        return self._Njk

    def __set_Njk(self, val):
        if (type(val) != int):
            raise ValueError("Number of subdivisions must be positive integer value")

        if (val <= 0):
            raise ValueError("Number of subdivisions must be positive integer value")

        self._Njk = val

    def __del_Njk(self):
        del self._Njk

    Njk = property(__get_Njk, __set_Njk, __del_Njk)

    # EleProps Validation
    def __get_EleProps(self):
        return self._EleProps

    def __set_EleProps(self, value):
        if type(value) != dict:
            raise ValueError('eleProps must be a python dictionary')


        self._EleProps = value

    def __del_EleProps(self):
        del self._EleProps

    EleProps = property(__get_EleProps, __set_EleProps, __del_EleProps)

    ## End of validation

    ###### loading ########################
    def assign_uniload(self, pattern, value, direction=3, coord='local', option='add'):

        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in [1, 2, 3]:
            raise ValueError('direction must be one of 1, 2 or 3')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        if coord.lower() not in ['global', 'g', 'local', 'l']:
            raise ValueError("coord must be \'global\', \'g\' or \'local\', \'l\'")

        uniloads = self.Uniload
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            self.Uniload = newuniloads
            return

        uniloads = self.Uniload
        newuniloads = []
        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            newuniloads.append([pattern, value, direction, coord])
            self.Uniload = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            if load[0]['Name'] == pattern['Name'] and load[2] == direction and load[3] == coord:
                if option.lower() in ['add', 'a']:
                    uniloads[i][1] += value
                    return

        uniloads.append([pattern, value, direction, coord])

    def __copy(self):
        newcomp = Quad(self.Name, self.EleProps, self.XYZi, self.XYZj, self.XYZk, self.XYZl, meshsize=self.Meshsize,
                       Nij=self.Nij, Njk=self.Njk)
        newcomp.Uniload = copy.deepcopy(self.Uniload)

        return newcomp
    ###### linear replicate ########################
    def replicate_linear(self, number, dx, dy, dz):
        if (type(number) != int):
            raise ValueError("Number of replications must be positive integer value")

        if (number <= 0):
            raise ValueError("Number of replications must be positive integer value")

        if isinstance(dx, numbers.Number) is False :
            raise ValueError('dx must be a numeric value')

        if isinstance(dy, numbers.Number) is False:
            raise ValueError('dy must be a numeric value')

        if isinstance(dz, numbers.Number) is False:
            raise ValueError('dz must be a numeric value')

        newcomponents = []
        name = self.Name
        xi, yi, zi = self.XYZi
        xj, yj, zj = self.XYZj
        xk, yk, zk = self.XYZk
        xl, yl, zl = self.XYZl
        for i in range(number):
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newxi, newyi, newzi  = xi + (i + 1) * dx, yi + (i + 1) * dy, zi + (i + 1) * dz
            newxj, newyj, newzj = xj + (i + 1) * dx, yj + (i + 1) * dy, zj + (i + 1) * dz
            newxk, newyk, newzk = xk + (i + 1) * dx, yk + (i + 1) * dy, zk + (i + 1) * dz
            newxl, newyl, newzl = xl + (i + 1) * dx, yl + (i + 1) * dy, zl + (i + 1) * dz
            newmember.XYZi = [newxi, newyi, newzi]
            newmember.XYZj = [newxj, newyj, newzj]
            newmember.XYZk = [newxk, newyk, newzk]
            newmember.XYZl = [newxl, newyl, newzl]
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### replicate mirror ########################
    def replicate_mirror(self, xyz1, xyz2, xyz3):
        name = self.Name
        newname = name + "_mir"
        newmember = self.__copy()
        newmember.XYZi = MyMath.mirrorpoint(self.XYZi, xyz1, xyz2, xyz3)
        newmember.XYZj = MyMath.mirrorpoint(self.XYZj, xyz1, xyz2, xyz3)
        newmember.XYZk = MyMath.mirrorpoint(self.XYZk, xyz1, xyz2, xyz3)
        newmember.XYZl = MyMath.mirrorpoint(self.XYZl, xyz1, xyz2, xyz3)
        newmember.Name = newname
        return newmember

    ###### replicate rotate ########################
    def replicate_rotate(self, number, xyz1, xyz2, teta):
        newcomponents = []
        name = self.Name
        for i in range(number):
            rot_t = teta * (i + 1)
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newmember.XYZi = MyMath.rotatepoint(self.XYZi, xyz1, xyz2, rot_t)
            newmember.XYZj = MyMath.rotatepoint(self.XYZj, xyz1, xyz2, rot_t)
            newmember.XYZk = MyMath.rotatepoint(self.XYZk, xyz1, xyz2, rot_t)
            newmember.XYZl = MyMath.rotatepoint(self.XYZl, xyz1, xyz2, rot_t)
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### Create Elements ########################
    def createelements(self):
        global _ndm
        eleProps = self.EleProps
        xyzi = self.XYZi
        xyzj = self.XYZj
        xyzk = self.XYZk
        xyzl = self.XYZl
        Nij = self.Nij
        Njk = self.Njk

        if self.Meshsize != 0.0:
            lij = np.sqrt(np.sum((np.array(xyzi) - np.array(xyzj))**2))
            ljk = np.sqrt(np.sum((np.array(xyzj) - np.array(xyzk))**2))
            lkl = np.sqrt(np.sum((np.array(xyzl) - np.array(xyzk)) ** 2))
            lil = np.sqrt(np.sum((np.array(xyzl) - np.array(xyzi)) ** 2))
            l1 = max([lij, lkl])
            l2 = max([ljk, lil])
            Nij = int(round(l1 / self.Meshsize))
            Njk = int(round(l2 / self.Meshsize))
            if Nij == 0:
                Nij = 1
            if Njk == 0:
                Njk = 1

        nodeTag = 1
        eleTag = 1

        if _ndm == 3:
            if len(xyzi) != 3 or len(xyzj) != 3 or len(xyzk) != 3 or len(xyzl) != 3:
                raise ValueError("ndm = 3: xyz should be a list contains coordinates [x, y, z]")
            xi, yi, zi = xyzi
            xj, yj, zj = xyzj
            xk, yk, zk = xyzk
            xl, yl, zl = xyzl
        else:
            if len(xyzi) < 2 or len(xyzj) < 2 or len(xyzk) < 2 or len(xyzl) < 2:
                raise ValueError("ndm = 2: xyz should be a list contains coordinates [x, y]")
            xi, yi = xyzi[0], xyzi[1]
            xj, yj = xyzj[0], xyzj[1]
            xk, yk = xyzk[0], xyzk[1]
            xl, yl = xyzl[0], xyzl[1]
            zi = zj = zk = zl = 0

        if eleProps['eleType'] in ['ShellNL', '9_4_QuadUP']:
            XX = np.zeros((2 * Njk + 1, 2 * Nij + 1))
            YY = np.zeros((2 * Njk + 1, 2 * Nij + 1))
            ZZ = np.zeros((2 * Njk + 1, 2 * Nij + 1))
            Noderange = np.zeros((2 * Njk + 1, 2 * Nij + 1))

            Xst = np.linspace(xi, xl, num=2 * Njk + 1)
            Xen = np.linspace(xj, xk, num=2 * Njk + 1)

            Yst = np.linspace(yi, yl, num=2 * Njk + 1)
            Yen = np.linspace(yj, yk, num=2 * Njk + 1)

            Zst = np.linspace(zi, zl, num=2 * Njk + 1)
            Zen = np.linspace(zj, zk, num=2 * Njk + 1)
        else:
            XX = np.zeros((Njk + 1, Nij + 1))
            YY = np.zeros((Njk + 1, Nij + 1))
            ZZ = np.zeros((Njk + 1, Nij + 1))
            Noderange = np.zeros((Njk + 1, Nij + 1))
            Xst = np.linspace(xi, xl, num=Njk + 1)
            Xen = np.linspace(xj, xk, num=Njk + 1)

            Yst = np.linspace(yi, yl, num=Njk + 1)
            Yen = np.linspace(yj, yk, num=Njk + 1)

            Zst = np.linspace(zi, zl, num=Njk + 1)
            Zen = np.linspace(zj, zk, num=Njk + 1)


        if eleProps['eleType'] in ['ShellNL', '9_4_QuadUP']:
            for i in range(0, 2 * Njk + 1):
                xrow = np.linspace(Xst[i], Xen[i], num=2 * Nij + 1)
                yrow = np.linspace(Yst[i], Yen[i], num=2 * Nij + 1)
                zrow = np.linspace(Zst[i], Zen[i], num=2 * Nij + 1)
                nraw = np.linspace(i * (2 * Nij + 1) + 1, i * (2 * Nij + 1) + 1 + 2 * Nij, num=2 * Nij + 1)
                XX[i, :] = xrow
                YY[i, :] = yrow
                ZZ[i, :] = zrow
                Noderange[i, :] = nraw
        else:
            for i in range(0, Njk + 1):
                xrow = np.linspace(Xst[i], Xen[i], num=Nij + 1)
                yrow = np.linspace(Yst[i], Yen[i], num=Nij + 1)
                zrow = np.linspace(Zst[i], Zen[i], num=Nij + 1)
                nraw = np.linspace(i * (Nij + 1) + 1, i * (Nij + 1) + 1 + Nij, num=Nij + 1)
                XX[i, :] = xrow
                YY[i, :] = yrow
                ZZ[i, :] = zrow
                Noderange[i, :] = nraw

        edgeNodes = []
        edgeNodes.append(list(Noderange[0]))
        edgeNodes.append(list(np.transpose(Noderange)[-1]))
        b = list(Noderange[-1])
        b.reverse()
        edgeNodes.append(b)
        b = list(np.transpose(Noderange)[0])
        b.reverse()
        edgeNodes.append(b)
        for i in range(len(edgeNodes)):
            edgeNodes[i] = [int(x) for x in edgeNodes[i]]

        Nodes = {}

        for i in np.arange(len(XX.reshape(-1))):
            x = XX.reshape(-1)[i]
            y = YY.reshape(-1)[i]
            z = ZZ.reshape(-1)[i]
            Nodes[nodeTag] = [x, y, z]
            nodeTag += 1

        # Extract Elements Node Tags
        Elements = {}
        if eleProps['eleType'] in ['ShellDKGT', 'ShellNLDKGT', 'Tri31']:
            for i in range(0, Njk):
                for j in range(1, Nij + 1):
                    nodei = i * (Nij + 1) + j
                    nodej = nodei + 1
                    nodek = nodej + (Nij + 1)
                    nodel = nodei + (Nij + 1)
                    Elements[eleTag] = [nodei, nodej, nodek]
                    eleTag += 1
                    Elements[eleTag] = [nodei, nodek, nodel]
                    eleTag += 1
        elif eleProps['eleType'] in ['quad', 'ShellMITC4', 'ShellDKGQ', 'ShellNLDKGQ', 'bbarQuad', 'enhancedQuad',
                                     'SSPquad']:
            for i in range(0, Njk):
                for j in range(1, Nij + 1):
                    nodei = i * (Nij + 1) + j
                    nodej = nodei + 1
                    nodek = nodej + (Nij + 1)
                    nodel = nodei + (Nij + 1)
                    Elements[eleTag] = [nodei, nodej, nodek, nodel]
                    eleTag += 1
        elif eleProps['eleType'] in ['ShellNL', '9_4_QuadUP']:
            for i in range(0, Njk):
                for j in range(1, 2 * Nij + 1, 2):
                    node1 = 2 * i * (2 * Nij + 1) + j
                    node2 = node1 + 2
                    node3 = node2 + 2 * (2 * Nij + 1)
                    node4 = node1 + 2 * (2 * Nij + 1)
                    node5 = node1 + 1
                    node6 = node2 + (2 * Nij + 1)
                    node7 = node3 - 1
                    node8 = node1 + (2 * Nij + 1)
                    node9 = node5 + (2 * Nij + 1)

                    Elements[eleTag] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                    eleTag += 1

        return Nodes, Elements, edgeNodes
        ## End of CreatePatches Function
class Triangle:
    def __init__(self, name, eleProps, xyzi, xyzj, xyzk, Ndiv=4):
        self.Name = name
        self.EleProps = eleProps
        self.XYZi = xyzi
        self.XYZj = xyzj
        self.XYZk = xyzk
        self.NDiv = Ndiv
        self.Uniload = []
        self.NodeSets = {'ij':[],'jk':[],'ki':[]}
        self.Nodes = {}
        self.Elements = {}
    ###### validation VBlock ( Set and Get Properties ) ########################
    def __get_name(self):
            return self._Name

    def __set_name(self, name):
        if type(name) is not str:
            raise ValueError("name must be string")
        self._Name = name

    def __del_name(self):
        del self._Name

    Name = property(__get_name, __set_name, __del_name)

    # XYZi
    def __get_XYZi(self):
        return self._XYZi

    def __set_XYZi(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)

        self._XYZi = value

    def __del_XYZi(self):
        del self._XYZi

    XYZi = property(__get_XYZi, __set_XYZi, __del_XYZi)

    # XYZj
    def __get_XYZj(self):
        return self._XYZj

    def __set_XYZj(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)

        self._XYZj = value

    def __del_XYZj(self):
        del self._XYZj

    XYZj = property(__get_XYZj, __set_XYZj, __del_XYZj)

    # XYZk
    def __get_XYZk(self):
        return self._XYZk

    def __set_XYZk(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)

        self._XYZk = value

    def __del_XYZk(self):
        del self._XYZk

    XYZk = property(__get_XYZk, __set_XYZk, __del_XYZk)

    # NDiv Validation
    def __get_NDiv(self):
        return self._NDiv

    def __set_NDiv(self, val):
        if (type(val) != int):
            raise ValueError("Number of subdivisions must be positive integer value")

        if (val <= 0):
            raise ValueError("Number of subdivisions must be positive integer value")

        self._NDiv = val

    def __del_NDiv(self):
        del self._NDiv

    NDiv = property(__get_NDiv, __set_NDiv, __del_NDiv)


    # EleProps Validation
    def __get_EleProps(self):
        return self._EleProps

    def __set_EleProps(self, value):
        if type(value) != dict:
            raise ValueError('eleProps must be a python dictionary')


        self._EleProps = value

    def __del_EleProps(self):
        del self._EleProps

    EleProps = property(__get_EleProps, __set_EleProps, __del_EleProps)

    ## End of validation

    ###### loading ########################
    def assign_uniload(self, pattern, value, direction=3, coord='local', option='add'):

        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in [1, 2, 3]:
            raise ValueError('direction must be one of 1, 2 or 3')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        if coord.lower() not in ['global', 'g', 'local', 'l']:
            raise ValueError("coord must be \'global\', \'g\' or \'local\', \'l\'")

        uniloads = self.Uniload
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            self.Uniload = newuniloads
            return

        uniloads = self.Uniload
        newuniloads = []
        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            newuniloads.append([pattern, value, direction, coord])
            self.Uniload = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            if load[0]['Name'] == pattern['Name'] and load[2] == direction and load[3] == coord:
                if option.lower() in ['add', 'a']:
                    uniloads[i][1] += value
                    return

        uniloads.append([pattern, value, direction, coord])

    def __copy(self):
        newcomp = Triangle(self.Name, self.EleProps, self.XYZi, self.XYZj , self.XYZk, Ndiv=self.NDiv)
        newcomp.Uniload = copy.deepcopy(self.Uniload)

        return newcomp
    ###### linear replicate ########################
    def replicate_linear(self, number, dx, dy, dz):
        if (type(number) != int):
            raise ValueError("Number of replications must be positive integer value")

        if (number <= 0):
            raise ValueError("Number of replications must be positive integer value")

        if isinstance(dx, numbers.Number) is False:
            raise ValueError('dx must be a numeric value')

        if isinstance(dy, numbers.Number) is False:
            raise ValueError('dy must be a numeric value')

        if isinstance(dz, numbers.Number) is False:
            raise ValueError('dz must be a numeric value')

        newcomponents = []
        name = self.Name
        xi, yi, zi = self.XYZi
        xj, yj, zj = self.XYZj
        xk, yk, zk = self.XYZk

        for i in range(number):
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newxi, newyi, newzi  = xi + (i + 1) * dx, yi + (i + 1) * dy, zi + (i + 1) * dz
            newxj, newyj, newzj = xj + (i + 1) * dx, yj + (i + 1) * dy, zj + (i + 1) * dz
            newxk, newyk, newzk = xk + (i + 1) * dx, yk + (i + 1) * dy, zk + (i + 1) * dz
            newmember.XYZi = [newxi, newyi, newzi]
            newmember.XYZj = [newxj, newyj, newzj]
            newmember.XYZk = [newxk, newyk, newzk]
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### replicate mirror ########################
    def replicate_mirror(self, xyz1, xyz2, xyz3):
        name = self.Name
        newname = name + "_mir"
        newmember = self.__copy()
        newmember.XYZi = MyMath.mirrorpoint(self.XYZi, xyz1, xyz2, xyz3)
        newmember.XYZj = MyMath.mirrorpoint(self.XYZj, xyz1, xyz2, xyz3)
        newmember.XYZk = MyMath.mirrorpoint(self.XYZk, xyz1, xyz2, xyz3)
        newmember.Name = newname
        return newmember

    ###### replicate rotate ########################
    def replicate_rotate(self, number, xyz1, xyz2, teta):
        newcomponents = []
        name = self.Name
        for i in range(number):
            rot_t = teta * (i + 1)
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newmember.XYZi = MyMath.rotatepoint(self.XYZi, xyz1, xyz2, rot_t)
            newmember.XYZj = MyMath.rotatepoint(self.XYZj, xyz1, xyz2, rot_t)
            newmember.XYZk = MyMath.rotatepoint(self.XYZk, xyz1, xyz2, rot_t)
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### Create Elements ########################
    def createelements(self):
        global _ndm
        eleProps = self.EleProps
        xyzi = self.XYZi
        xyzj = self.XYZj
        xyzk = self.XYZk
        N = self.NDiv

        if _ndm == 3:
            if len(xyzi) != 3 or len(xyzj) != 3 or len(xyzk) != 3:
                raise ValueError("ndm = 3: xyz should be a list contains coordinates [x, y, z]")

        else:
            if len(xyzi) < 2 or len(xyzj) < 2 or len(xyzk) < 2:
                raise ValueError("ndm = 2: xyz should be a list contains coordinates [x, y]")
            xyzi = [xyzi[0], xyzi[1], 0]
            xyzj = [xyzj[0], xyzj[1], 0]
            xyzk = [xyzk[0], xyzk[1], 0]

        # Extract Elements Node Tags
        ele_numnodes = 4
        if eleProps['eleType'] in ['ShellDKGT', 'ShellNLDKGT', 'Tri31']:
            ele_numnodes = 3

        elif eleProps['eleType'] in ['ShellNL', '9_4_QuadUP']:
            ele_numnodes = 9

        Nodes, Elements, aedgeNodes = MyMath.dividetriangle(N, ele_numnodes, xyzi, xyzj, xyzk)
        edgeNodes = [list(aedgeNodes['ij']), list(aedgeNodes['jk']), list(aedgeNodes['ki'])]

        for i in range(len(edgeNodes)):
            edgeNodes[i] = [int(x) for x in edgeNodes[i]]

        return Nodes, Elements, edgeNodes
        ## End of CreatePatches Function

class Line:
    def __init__(self, name, eleProps, xyzi, xyzj, meshsize=0.0, Ndiv=1):
        self.Name = name
        self.EleProps = eleProps
        self.XYZi = xyzi
        self.XYZj = xyzj
        self.NDiv = Ndiv
        self.Meshsize = meshsize
        self.Uniload = []
        self.Pointload = []
        self.NodeSets = {'i': 0, 'j': 0}
        self.Nodes = {}
        self.Elements = {}

    ###### alidation VBlock ( Set and Get Properties ) ########################
    def __get_name(self):
            return self._Name

    def __set_name(self, name):
        if type(name) is not str:
            raise ValueError("name must be string")
        self._Name = name

    def __del_name(self):
        del self._Name

    Name = property(__get_name, __set_name, __del_name)

    # XYZi
    def __get_XYZi(self):
        return self._XYZi

    def __set_XYZi(self, value):
        if isinstance(value, Point):
            value = value.XYZ

        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])
            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)

        self._XYZi = value

    def __del_XYZi(self):
        del self._XYZi

    XYZi = property(__get_XYZi, __set_XYZi, __del_XYZi)

    # XYZj
    def __get_XYZj(self):
        return self._XYZj

    def __set_XYZj(self, value):
        if isinstance(value, Point):
            value = value.XYZ
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)

        self._XYZj = value

    def __del_XYZj(self):
        del self._XYZj

    XYZj = property(__get_XYZj, __set_XYZj, __del_XYZj)

    # NDiv Validation
    def __get_NDiv(self):
        return self._NDiv

    def __set_NDiv(self, val):
        if (type(val) != int):
            raise ValueError("Number of subdivisions must be positive integer value")

        if (val <= 0):
            raise ValueError("Number of subdivisions must be positive integer value")

        self._NDiv = val

    def __del_NDiv(self):
        del self._NDiv

    NDiv = property(__get_NDiv, __set_NDiv, __del_NDiv)

    # EleProps Validation
    def __get_EleProps(self):
        return self._EleProps

    def __set_EleProps(self, value):
        if type(value) != dict:
            raise ValueError('eleProps must be a python dictionary')

        self._EleProps = value

    def __del_EleProps(self):
        del self._EleProps

    EleProps = property(__get_EleProps, __set_EleProps, __del_EleProps)

    ## End of validation
    ###### Assign Loads ########################
    def assign_uniload(self, pattern, value, direction=2, coord='global',  option='add'):
        '''
        Function to assign uniform load on Line components.
        pattern: Dictinary
                 A dictionary contains load pattern properties
        values: float or list of float numbers
                 Load value or a list contains load values
        directions: int or list of integer numbers
                Line element local axis direction or a list contains directions. It can be 1, 2 or 3 or a list of them.
        option: str
                Can be 'add'('a') or 'replace'('r') to define if load will be added or replaced with new value based on
                pattern name and direction. Default value is 'add'
        return: None
        '''

        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in [1, 2, 3]:
            raise ValueError('direction must be one of 1, 2 or 3')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        if coord.lower() not in ['global', 'g', 'local', 'l']:
            raise ValueError("coord must be \'global\', \'g\' or \'local\', \'l\'")

        uniloads = self.Uniload
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            self.Uniload = newuniloads
            return

        uniloads = self.Uniload
        newuniloads = []
        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            newuniloads.append([pattern, value, direction, coord])
            self.Uniload = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            if load[0]['Name'] == pattern['Name'] and load[2] == direction and load[3] == coord:
                if option.lower() in ['add', 'a']:
                    uniloads[i][1] += value
                    return

        uniloads.append([pattern, value, direction, coord])

    # def assign_pointload(self, pattern, *distvalue, direction=2):
    #     poloads = self.Pointload
    #     poloads.append([pattern, distvalue, direction])
    def __copy(self):
        newcomp = Line(self.Name, self.EleProps, self.XYZi, self.XYZj,meshsize=self.Meshsize, Ndiv=self.NDiv)
        newcomp.Uniload = copy.deepcopy(self.Uniload)
        newcomp.Pointload = copy.deepcopy(self.Pointload)

        return newcomp

    ###### linear replicate ########################
    def replicate_linear(self, number, dx, dy, dz):
        if (type(number) != int):
            raise ValueError("Number of replications must be positive integer value")

        if (number <= 0):
            raise ValueError("Number of replications must be positive integer value")

        if isinstance(dx, numbers.Number) is False:
            raise ValueError('dx must be a numeric value')

        if isinstance(dy, numbers.Number) is False:
            raise ValueError('dy must be a numeric value')

        if isinstance(dz, numbers.Number) is False:
            raise ValueError('dz must be a numeric value')

        newcomponents = []
        name = self.Name
        xi, yi, zi = self.XYZi
        xj, yj, zj = self.XYZj
        for i in range(number):
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newxi, newyi, newzi = xi + (i + 1) * dx, yi + (i + 1) * dy, zi + (i + 1) * dz
            newxj, newyj, newzj = xj + (i + 1) * dx, yj + (i + 1) * dy, zj + (i + 1) * dz
            newmember.XYZi = [newxi, newyi, newzi]
            newmember.XYZj = [newxj, newyj, newzj]
            newmember.Name = newname
            newcomponents.append(newmember)
        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### replicate mirror ########################
    def replicate_mirror(self, xyz1, xyz2, xyz3):
        name = self.Name
        newname = name + "_mir"
        newmember = self.__copy()
        newmember.XYZi = MyMath.mirrorpoint(self.XYZi, xyz1, xyz2, xyz3)
        newmember.XYZj = MyMath.mirrorpoint(self.XYZj, xyz1, xyz2, xyz3)
        newmember.Name = newname
        return newmember

    ###### replicate rotate ########################
    def replicate_rotate(self, number, xyz1, xyz2, teta):
        newcomponents = []
        name = self.Name
        for i in range(number):
            rot_t = teta * (i + 1)
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newmember.XYZi = MyMath.rotatepoint(self.XYZi, xyz1, xyz2, rot_t)
            newmember.XYZj = MyMath.rotatepoint(self.XYZj, xyz1, xyz2, rot_t)
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### Create Elements ########################
    def createelements(self):
        global _ndm
        eleProps = self.EleProps
        xyzi = self.XYZi
        xyzj = self.XYZj
        Nij = self.NDiv

        if self.Meshsize != 0.0:
            lij = np.sqrt(np.sum((np.array(xyzi) - np.array(xyzj))**2))
            Nij = int(round(lij / self.Meshsize))
            if Nij == 0:
                Nij = 1

        nodeTag = 1
        eleTag = 1

        if eleProps['eleType'] in ['ModElasticBeam2d']:
            if _ndm == 3:
                raise ValueError("Using ModElasticBeam2d element: ndm must to 2")

        if _ndm == 3:
            if len(xyzi) != 3 or len(xyzj) != 3:
                raise ValueError("ndm = 3: xyz should be a list contains coordinates [x, y, z]")
            xi, yi, zi = xyzi
            xj, yj, zj = xyzj

        else:
            if len(xyzi) < 2 or len(xyzj) < 2:
                raise ValueError("ndm = 2: xyz should be a list contains coordinates [x, y]")
            xi, yi = xyzi[0], xyzi[1]
            xj, yj = xyzj[0], xyzj[1]
            zi = zj = 0


        XX = np.linspace(xi, xj, num=Nij + 1)
        YY = np.linspace(yi, yj, num=Nij + 1)
        ZZ = np.linspace(zi, zj, num=Nij + 1)
        edgeNodes = [1, Nij + 1]

        Nodes = {}

        for i in np.arange(len(XX)):
            x = XX[i]
            y = YY[i]
            z = ZZ[i]
            Nodes[nodeTag] = [x, y, z]
            nodeTag += 1

        # Extract Elements Node Tags
        Elements = {}

        for i in range(1, Nij + 1):
            nodei = i
            nodej = nodei + 1
            Elements[eleTag] = [nodei, nodej]
            eleTag += 1

        return Nodes, Elements, edgeNodes
        ## End of CreatePatches Function

class Point:
    def __init__(self, name, xyz, mass=[], rest=[]):
        self.XYZ = xyz
        self.Name = name
        self.NodeTag = 0
        self.Nodes = {}
        self.Pointload = []
        self.Mass = mass
        self.Rest = rest
    ###### alidation VBlock ( Set and Get Properties ) ########################
    def __get_name(self):
            return self._Name

    def __set_name(self, name):
        if type(name) is not str:
            raise ValueError("name must be string")
        self._Name = name

    def __del_name(self):
        del self._Name

    Name = property(__get_name, __set_name, __del_name)

    # XYZ
    def __get_XYZ(self):
        return self._XYZ

    def __set_XYZ(self, value):
        value = list(value)
        if len(value) not in [2, 3]:
            raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

        for i in range(len(value)):
            if type(value[i]) is int:
                value[i] = float(value[i])

            if isinstance(value[i], numbers.Number) is False:
                raise ValueError("Coordinates must be numeric values")
        if len(value) == 2:
            value.append(0.0)

        self._XYZ = value

    def __del_XYZ(self):
        del self._XYZ

    XYZ = property(__get_XYZ, __set_XYZ, __del_XYZ)

    ## End of validation

    def assign_pointload(self, pattern, value, direction, option='add'):
        global _ndf
        dirvals = list(np.arange(1, _ndf+1, dtype=int))
        if isinstance(value, numbers.Number) is False:
            raise ValueError('value must be a numeric value')

        if direction not in [1, 2, 3]:
            raise ValueError('direction must be one of 1, 2 or 3')

        if option.lower() not in ['add', 'a', 'replace', 'r', 'delete', 'd']:
            raise ValueError("option must be \'add\', \'a\' or \'replace\', \'r\' or \'delete\', \'d\' ")

        uniloads = self.Pointload
        newuniloads = []
        if option.lower() in ['delete', 'd']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            self.Pointload = newuniloads
            return

        if option.lower() in ['replace', 'r']:
            for i in range(len(uniloads)):
                load = uniloads[i]
                if load[0]['Name'] != pattern['Name']:
                    newuniloads.append(load)

            newuniloads.append([pattern, value, direction])
            self.Pointload = newuniloads
            return

        for i in range(len(uniloads)):
            load = uniloads[i]
            if load[0]['Name'] == pattern['Name'] and load[2] == direction:
                if option.lower() in ['add', 'a']:
                    uniloads[i][1] += value
                    return

        uniloads.append([pattern, value, direction])

    def __copy(self):
        newcomp = Point(self.Name, self.XYZ, mass=self.Mass, rest=self.Rest)
        newcomp.Pointload = copy.deepcopy(self.Pointload)

        return newcomp

    ###### linear replicate ########################
    def replicate_linear(self, number, dx, dy, dz):
        if (type(number) != int):
            raise ValueError("Number of replications must be positive integer value")

        if (number <= 0):
            raise ValueError("Number of replications must be positive integer value")

        if isinstance(dx, numbers.Number) is False:
            raise ValueError('dx must be a numeric value')

        if isinstance(dy, numbers.Number) is False:
            raise ValueError('dy must be a numeric value')

        if isinstance(dz, numbers.Number) is False:
            raise ValueError('dz must be a numeric value')

        newcomponents = []
        name = self.Name
        x, y, z = self.XYZ
        for i in range(number):
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newx, newy, newz = x + (i + 1) * dx, y + (i + 1) * dy, z + (i + 1) * dz
            newmember.XYZ = [newx, newy, newz]
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    ###### replicate mirror ########################
    def replicate_mirror(self, xyz1, xyz2, xyz3):
        name = self.Name
        newname = name + "_mir"
        newmember = self.__copy()
        newmember.XYZ = MyMath.mirrorpoint(self.XYZ, xyz1, xyz2, xyz3)
        newmember.Name = newname
        return newmember

    ###### replicate rotate ########################
    def replicate_rotate(self, number, xyz1, xyz2, teta):
        newcomponents = []
        name = self.Name
        for i in range(number):
            rot_t = teta * (i + 1)
            newname = name + "_" + str(i + 1)
            newmember = self.__copy()
            newmember.XYZ = MyMath.rotatepoint(self.XYZ, xyz1, xyz2, rot_t)
            newmember.Name = newname
            newcomponents.append(newmember)

        if number == 1:
            return newcomponents[0]
        else:
            return newcomponents

    # ###### Create Elements ########################
    # def create_node(self):
    #     global _ndm
    #     xyz = self.XYZ
    #     nodeTag = 1
    #     eleTag = 1
    #
    #     if _ndm == 3:
    #         if len(xyz) != 3:
    #             raise ValueError("_ndm = 3: xyz should be a list contains coordinates [x, y, z]")
    #         x, y, z = xyz
    #
    #     else:
    #         if len(xyzi) < 2 or len(xyzj) < 2 :
    #             raise ValueError("_ndm = 2: xyz should be a list contains coordinates [x, y]")
    #         xi, yi = xyzi[0], xyzi[1]
    #         xj, yj = xyzj[0], xyzj[1]
    #         zi = zj = 0
    #
    #
    #     XX = np.linspace(xi, xj, num=Nij + 1)
    #     YY = np.linspace(yi, yj, num=Nij + 1)
    #     ZZ = np.linspace(zi, zj, num=Nij + 1)
    #     edgeNodes = [1, Nij + 1]
    #
    #     Nodes = {}
    #
    #     for i in np.arange(len(XX)):
    #         x = XX[i]
    #         y = YY[i]
    #         z = ZZ[i]
    #         Nodes[nodeTag] = [x, y, z]
    #         nodeTag += 1
    #
    #     # Extract Elements Node Tags
    #     Elements = {}
    #
    #     for i in range(1, Nij + 1):
    #         nodei = i
    #         nodej = nodei + 1
    #         Elements[eleTag] = [nodei, nodej]
    #         eleTag += 1
    #
    #     return Nodes, Elements, edgeNodes
    #     ## End of CreatePatches Function

### Class point]

def create_node(ops, xyz, print_command):
    global _ndm
    global _name
    exnode = nodeexist(ops, xyz)
    if exnode != False:
        print("# Note:")
        print("#    Node " + str(exnode) + " exists at this location.")

    nodeTag = int(np.max(ops.getNodeTags())) + 1
    if _ndm == 2:
        str_command = "ops.node(" + str(int(nodeTag)) + ", " + str(xyz[0]) + ", " + str(xyz[1]) + ")"

    elif _ndm == 3:
        str_command = "ops.node(" + str(int(nodeTag)) + ", " + str(xyz[0]) + ", " + str(xyz[1]) + ", " + str(xyz[2]) + ")"

    if print_command.lower() in ['y', 'yes']:
        print(str_command)

    eval(str_command)
    file_nodes = open(_name + "\\" + "file_nodes.txt", "a")
    file_nodes.write(str_command + '\n')
    file_nodes.close()
    return nodeTag

def copy_component(component, newname):
    newmember = copy.deepcopy(component)
    newmember.Name = newname
    return newmember
def plot_localcoords(ax, *parts):
    for part in parts:
        for component in part.Components:
            plot_localcoord(ax, component)

def plot_component(ax, component, name = 'n' , propname='y', subdivisions = 'y', localcoord='n', linewidth=0.2,
                   pointsize=0.2, edgelinewidth = 0.2, fill='y', coloring='default',
                          fontsize=3,xlim=[], ylim=[],zlim=[], facenumber='n', alpha=0.5):

    for arg in [name, subdivisions, fill, propname]:
        if arg not in ['yes', 'y', 'no', 'n']:
            raise ValueError("name and subdivisions can "
                             "be \"yes\", \"y\",  \"no\" or \"n\" ")

    if coloring not in ['default', 'eleProps', 'eleType']:
        print('coloring can be  \'default\' or \'eleProps\' or \'eleType\'. default will be used ')
        coloring = 'default'

    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []

    if isinstance(component, Point):
        xyz = component.XYZ
        plot_ele = True
        if len(xlim) != 0:
            for xx in [xyz[0]]:
                if xx < xlim[0] or xx > xlim[1]:
                    plot_ele = False
        if len(ylim) != 0:
            for yy in [xyz[1]]:
                if yy < ylim[0] or yy > ylim[1]:
                    plot_ele = False
        if len(zlim) != 0:
            for zz in [xyz[2]]:
                if zz < zlim[0] or zz > zlim[1]:
                    plot_ele = False

        if plot_ele is False:
            return

        x = [xyz[0]]
        y = [xyz[1]]
        z = [xyz[2]]

        if name.lower() in ['y', 'yes']:
            ax.text(x, y, z, component.Name, '', size=fontsize, horizontalalignment='center')
        co = 'blue'
        ax.scatter(z, x, y, c=co, s=pointsize, alpha=0.7)

        return

    Nodes, Elements, nodeset = component.createelements()
    if isinstance(component, Brick):

        xyz1 = component.XYZ1
        xyz2 = component.XYZ2
        xyz3 = component.XYZ3
        xyz4 = component.XYZ4
        xyz5 = component.XYZ5
        xyz6 = component.XYZ6
        xyz7 = component.XYZ7
        xyz8 = component.XYZ8

        plot_ele = True
        if len(xlim) != 0:
            for xx in [xyz1[0], xyz2[0], xyz3[0], xyz4[0], xyz5[0], xyz6[0], xyz7[0], xyz8[0]]:
                if xx < xlim[0] or xx > xlim[1]:
                    plot_ele = False
        if len(ylim) != 0:
            for yy in [xyz1[1], xyz2[1], xyz3[1], xyz4[1], xyz5[1], xyz6[1], xyz7[1], xyz8[1]]:
                if yy < ylim[0] or yy > ylim[1]:
                    plot_ele = False
        if len(zlim) != 0:
            for zz in [xyz1[2], xyz2[2], xyz3[2], xyz4[2], xyz5[2], xyz6[2], xyz7[2], xyz8[2]]:
                if zz < zlim[0] or zz > zlim[1]:
                    plot_ele = False

        if plot_ele is False:
            return
        if localcoord.lower() in ['y', 'yes']:
            plot_localcoord(ax, component)

        co = 'lightskyblue'
        if coloring == 'eleProps':
            co = component.EleProps['Color']
        elif coloring == 'eleType':
            co = 'lightskyblue'
            # if component.EleProps['eleType'] == 'Tri31':
            #     co = 'springgreen'
            # elif component.EleProps['eleType'] in ['ShellMITC4', 'ShellNL', 'ShellDKGQ', 'ShellDKGT', 'ShellNLDKGQ',
            #                                     'ShellNLDKGT']:
            #     co = 'silver'
            # elif component.EleProps['eleType'] in ['bbarQuad', 'quad', 'enhancedQuad',
            #                                     'SSPquad']:
            #     co = 'blueviolet'
        MyMath.plotbrickmember(ax, component, name, propname, subdivisions, edgelinewidth, fill, co, fontsize,facenumber, alpha)

    elif isinstance(component, Polygon):

        xyz = component.XYZ
        XX = []
        YY = []
        ZZ = []
        for coords in xyz:
            XX.append(coords[0])
            YY.append(coords[1])
            ZZ.append(coords[2])
        plot_ele = True
        if len(xlim) != 0:
            for xx in XX:
                if xx < xlim[0] or xx > xlim[1]:
                    plot_ele = False
        if len(ylim) != 0:
            for yy in YY:
                if yy < ylim[0] or yy > ylim[1]:
                    plot_ele = False
        if len(zlim) != 0:
            for zz in ZZ:
                if zz < zlim[0] or zz > zlim[1]:
                    plot_ele = False

        if plot_ele is False:
            return

        if localcoord.lower() in ['y', 'yes']:
            plot_localcoord(ax, component)

        if subdivisions.lower() in ['y', 'yes']:
            for ele in Elements.keys():
                if len(Elements[ele]) in [4, 9]:
                    nodei = Elements[ele][0]
                    nodej = Elements[ele][1]
                    nodek = Elements[ele][2]
                    nodel = Elements[ele][3]

                    x = [Nodes[nodei][0], Nodes[nodej][0], Nodes[nodek][0], Nodes[nodel][0], Nodes[nodei][0]]
                    y = [Nodes[nodei][1], Nodes[nodej][1], Nodes[nodek][1], Nodes[nodel][1], Nodes[nodei][1]]
                    z = [Nodes[nodei][2], Nodes[nodej][2], Nodes[nodek][2], Nodes[nodel][2], Nodes[nodei][2]]
                elif len(Elements[ele]) == 3:
                    nodei = Elements[ele][0]
                    nodej = Elements[ele][1]
                    nodek = Elements[ele][2]
                    x = [Nodes[nodei][0], Nodes[nodej][0], Nodes[nodek][0], Nodes[nodei][0]]
                    y = [Nodes[nodei][1], Nodes[nodej][1], Nodes[nodek][1], Nodes[nodei][1]]
                    z = [Nodes[nodei][2], Nodes[nodej][2], Nodes[nodek][2], Nodes[nodei][2]]

                ax.plot(z, x, y, linewidth=edgelinewidth, color='tab:gray')

        if name.lower() in ['y', 'yes']:
            xa = np.average(XX)
            ya = np.average(YY)
            za = np.average(ZZ)
            ax.text(za, xa, ya, component.Name, 'y', size=fontsize, horizontalalignment='center')

        if propname.lower() in ['y', 'yes']:
            prname = component.EleProps['Name']
            xa = np.average(XX)
            ya = np.average(YY)
            za = np.average(ZZ)
            ax.text(za, xa, ya, prname, 'y', size=fontsize, horizontalalignment='center')

        if coloring == 'default':
            co = 'lightskyblue'
        elif coloring == 'eleProps':
            co = component.EleProps['Color']
        elif coloring == 'eleType':
            co = 'lightskyblue'
            if component.EleProps['eleType'] == 'Tri31':
                co = 'springgreen'
            elif component.EleProps['eleType'] in ['ShellMITC4', 'ShellNL', 'ShellDKGQ', 'ShellDKGT', 'ShellNLDKGQ',
                                                'ShellNLDKGT']:
                co = 'silver'
            elif component.EleProps['eleType'] in ['bbarQuad', 'quad', 'enhancedQuad',
                                                'SSPquad']:
                co = 'blueviolet'

        if fill.lower() in ['y', 'yes']:
            vertices = [list(zip(ZZ, XX, YY))]
            poly = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=co, edgecolor='silver')
            ax.add_collection3d(poly)

        x = XX
        x.append(XX[0])
        y = YY
        y.append(YY[0])
        z = ZZ
        z.append(ZZ[0])
        ax.plot(z, x, y, lw=edgelinewidth, color='silver')

    elif isinstance(component, Quad):

        xyzi = component.XYZi
        xyzj = component.XYZj
        xyzk = component.XYZk
        xyzl = component.XYZl
        plot_ele = True
        if len(xlim) != 0:
            for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
                if xx < xlim[0] or xx > xlim[1]:
                    plot_ele = False
        if len(ylim) != 0:
            for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
                if yy < ylim[0] or yy > ylim[1]:
                    plot_ele = False
        if len(zlim) != 0:
            for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
                if zz < zlim[0] or zz > zlim[1]:
                    plot_ele = False

        if plot_ele is False:
            return

        if localcoord.lower() in ['y', 'yes']:
            plot_localcoord(ax, component)

        if subdivisions.lower() in ['y', 'yes']:
            for ele in Elements.keys():
                if len(Elements[ele]) in [4, 9]:
                    nodei = Elements[ele][0]
                    nodej = Elements[ele][1]
                    nodek = Elements[ele][2]
                    nodel = Elements[ele][3]
                    x = [Nodes[nodei][0], Nodes[nodej][0], Nodes[nodek][0], Nodes[nodel][0], Nodes[nodei][0]]
                    y = [Nodes[nodei][1], Nodes[nodej][1], Nodes[nodek][1], Nodes[nodel][1], Nodes[nodei][1]]
                    z = [Nodes[nodei][2], Nodes[nodej][2], Nodes[nodek][2], Nodes[nodel][2], Nodes[nodei][2]]
                elif len(Elements[ele]) == 3:
                    nodei = Elements[ele][0]
                    nodej = Elements[ele][1]
                    nodek = Elements[ele][2]
                    x = [Nodes[nodei][0], Nodes[nodej][0], Nodes[nodek][0], Nodes[nodei][0]]
                    y = [Nodes[nodei][1], Nodes[nodej][1], Nodes[nodek][1], Nodes[nodei][1]]
                    z = [Nodes[nodei][2], Nodes[nodej][2], Nodes[nodek][2], Nodes[nodei][2]]

                ax.plot(z, x, y, linewidth=edgelinewidth, color='tab:gray')

        if name.lower() in ['y', 'yes']:
            xa = np.average([xyzi[0], xyzj[0], xyzk[0], xyzl[0]])
            ya = np.average([xyzi[1], xyzj[1], xyzk[1], xyzl[1]])
            za = np.average([xyzi[2], xyzj[2], xyzk[2], xyzl[2]])
            ax.text(za, xa, ya, component.Name, 'y', size=fontsize, horizontalalignment='center')

        if propname.lower() in ['y', 'yes']:
            prname = component.EleProps['Name']
            xa = np.average([xyzi[0], xyzj[0], xyzk[0], xyzl[0]])
            ya = np.average([xyzi[1], xyzj[1], xyzk[1], xyzl[1]])
            za = np.average([xyzi[2], xyzj[2], xyzk[2], xyzl[2]])
            ax.text(za, xa, ya, prname, 'y', size=fontsize, horizontalalignment='center')

        if coloring == 'default':
            co = 'lightskyblue'
        elif coloring == 'eleProps':
            co = component.EleProps['Color']
        elif coloring == 'eleType':
            co = 'lightskyblue'
            if component.EleProps['eleType'] == 'Tri31':
                co = 'springgreen'
            elif component.EleProps['eleType'] in ['ShellMITC4', 'ShellNL', 'ShellDKGQ', 'ShellDKGT', 'ShellNLDKGQ',
                                                'ShellNLDKGT']:
                co = 'silver'
            elif component.EleProps['eleType'] in ['bbarQuad', 'quad', 'enhancedQuad',
                                                'SSPquad']:
                co = 'blueviolet'


        if fill.lower() in ['n', 'no']:
            alpha = 0.0

        p1 = [xyzi[2], xyzi[0],xyzi[1]]
        p2 = [xyzj[2], xyzj[0], xyzj[1]]
        p3 = [xyzk[2], xyzk[0], xyzk[1]]
        p4 = [xyzl[2], xyzl[0], xyzl[1]]
        MyMath.plot_area(ax, p1, p2, p3, p4, alpha=alpha, linewidth=edgelinewidth, color=co, edgecolor='silver', sha=False)

    elif isinstance(component, Triangle):

        xyzi = component.XYZi
        xyzj = component.XYZj
        xyzk = component.XYZk

        plot_ele = True
        if len(xlim) != 0:
            for xx in [xyzi[0], xyzj[0], xyzk[0]]:
                if xx < xlim[0] or xx > xlim[1]:
                    plot_ele = False
        if len(ylim) != 0:
            for yy in [xyzi[1], xyzj[1], xyzk[1]]:
                if yy < ylim[0] or yy > ylim[1]:
                    plot_ele = False
        if len(zlim) != 0:
            for zz in [xyzi[2], xyzj[2], xyzk[2]]:
                if zz < zlim[0] or zz > zlim[1]:
                    plot_ele = False

        if plot_ele is False:
            return

        if localcoord.lower() in ['y', 'yes']:
            plot_localcoord(ax, component)

        if subdivisions.lower() in ['y', 'yes']:
            for ele in Elements.keys():
                if len(Elements[ele]) in [4, 9]:
                    nodei = Elements[ele][0]
                    nodej = Elements[ele][1]
                    nodek = Elements[ele][2]
                    nodel = Elements[ele][3]
                    x = [Nodes[nodei][0], Nodes[nodej][0], Nodes[nodek][0], Nodes[nodel][0], Nodes[nodei][0]]
                    y = [Nodes[nodei][1], Nodes[nodej][1], Nodes[nodek][1], Nodes[nodel][1], Nodes[nodei][1]]
                    z = [Nodes[nodei][2], Nodes[nodej][2], Nodes[nodek][2], Nodes[nodel][2], Nodes[nodei][2]]
                elif len(Elements[ele]) == 3:
                    nodei = Elements[ele][0]
                    nodej = Elements[ele][1]
                    nodek = Elements[ele][2]
                    x = [Nodes[nodei][0], Nodes[nodej][0], Nodes[nodek][0], Nodes[nodei][0]]
                    y = [Nodes[nodei][1], Nodes[nodej][1], Nodes[nodek][1], Nodes[nodei][1]]
                    z = [Nodes[nodei][2], Nodes[nodej][2], Nodes[nodek][2], Nodes[nodei][2]]

                ax.plot(z, x, y, linewidth=edgelinewidth, color='tab:gray')

        if name.lower() in ['y', 'yes']:
            xa = np.average([xyzi[0], xyzj[0], xyzk[0]])
            ya = np.average([xyzi[1], xyzj[1], xyzk[1]])
            za = np.average([xyzi[2], xyzj[2], xyzk[2]])
            ax.text(za, xa, ya, component.Name, 'y', size=fontsize, horizontalalignment='center')

        if propname.lower() in ['y', 'yes']:
            prname = component.EleProps['Name']
            xa = np.average([xyzi[0], xyzj[0], xyzk[0]])
            ya = np.average([xyzi[1], xyzj[1], xyzk[1]])
            za = np.average([xyzi[2], xyzj[2], xyzk[2]])
            ax.text(za, xa, ya, prname, 'y', size=fontsize, horizontalalignment='center')

        if coloring == 'default':
            co = 'lightskyblue'
        elif coloring == 'eleProps':
            co = component.EleProps['Color']
        elif coloring == 'eleType':
            co = 'lightskyblue'
            if component.EleProps['eleType'] == 'Tri31':
                co = 'springgreen'
            elif component.EleProps['eleType'] in ['ShellMITC4', 'ShellNL', 'ShellDKGQ', 'ShellDKGT', 'ShellNLDKGQ',
                                                'ShellNLDKGT']:
                co = 'silver'
            elif component.EleProps['eleType'] in ['bbarQuad', 'quad', 'enhancedQuad',
                                                'SSPquad']:
                co = 'blueviolet'

        if fill.lower() in ['n', 'no']:
            alpha = 0.0

        p1 = [xyzi[2], xyzi[0],xyzi[1]]
        p2 = [xyzj[2], xyzj[0], xyzj[1]]
        p3 = [xyzk[2], xyzk[0], xyzk[1]]
        MyMath.plot_area(ax, p1, p2, p3, alpha=alpha, linewidth=edgelinewidth, color=co, edgecolor='silver', sha=False)

    elif isinstance(component, Line):

        xyzi = component.XYZi
        xyzj = component.XYZj
        plot_ele = True
        if len(xlim) != 0:
            for xx in [xyzi[0], xyzj[0]]:
                if xx < xlim[0] or xx > xlim[1]:
                    plot_ele = False
        if len(ylim) != 0:
            for yy in [xyzi[1], xyzj[1]]:
                if yy < ylim[0] or yy > ylim[1]:
                    plot_ele = False
        if len(zlim) != 0:
            for zz in [xyzi[2], xyzj[2]]:
                if zz < zlim[0] or zz > zlim[1]:
                    plot_ele = False

        if plot_ele is False:
            return

        if localcoord.lower() in ['y', 'yes']:
            plot_localcoord(ax, component)

        x = [xyzi[0], xyzj[0]]
        y = [xyzi[1], xyzj[1]]
        z = [xyzi[2], xyzj[2]]
        dirz = [xyzj[2] - xyzi[2], xyzj[0] - xyzi[0], xyzj[1] - xyzi[1]]
        if name.lower() in ['y', 'yes']:
            xa = np.average([xyzi[0], xyzj[0]])
            ya = np.average([xyzi[1], xyzj[1]])
            za = np.average([xyzi[2], xyzj[2]])
            ax.text(za, xa, ya, component.Name, dirz, size=fontsize, horizontalalignment='center')

        if propname.lower() in ['y', 'yes']:
            prname = component.EleProps['Name']
            xa = np.average([xyzi[0], xyzj[0]])
            ya = np.average([xyzi[1], xyzj[1]])
            za = np.average([xyzi[2], xyzj[2]])
            ax.text(za, xa, ya, prname, dirz, size=fontsize, horizontalalignment='center')


        if coloring == 'default':
            co = 'royalblue'
        elif coloring == 'eleProps':
            co = component.EleProps['Color']
        elif coloring == 'eleType':
            co = 'royalblue'
            if component.EleProps['eleType'] == 'twoNodeLink':
                co = 'springgreen'
            elif component.EleProps['eleType'] in ['Truss', 'TrussSection', 'corotTruss', 'corotTrussSection']:
                co = 'darkorange'
            elif component.EleProps['eleType'] in ['elasticBeamColumn', 'elasticBeamColumnSec', 'ModElasticBeam2d', 'ElasticTimoshenkoBeam']:
                co = 'blueviolet'
            elif component.EleProps['eleType'] in ['dispBeamColumn']:
                co = 'seagreen'
            elif component.EleProps['eleType'] in ['forceBeamColumn', 'nonlinearBeamColumn']:
                co = 'royalblue'


        ax.plot(z, x, y, lw=linewidth, color=co)

    ax.axis('equal')

def plot_opsmodel(ops, ax, elements='y', eletag='n', nodes='y', nodetag='n', linewidth=0.7, edgelinewidth=0.3,
                  nodesize=1.0, nodecolor='g', fill='y', fontsize=3, xlim=[], ylim=[], zlim=[], spconst='y',
                  rigiddiaph='y', alpha=0.9):
    global _ndm
    for arg in [nodes, eletag, fill, nodetag, elements]:
        if arg not in ['yes', 'y', 'no', 'n']:
            raise ValueError("name and subdivisions can "
                             "be \"yes\", \"y\",  \"no\" or \"n\" ")

    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []


    if os.path.exists('mymodel.txt'):
        os.remove('mymodel.txt')

   ### Plot Nodes
    plotednodes = []
    plotednodes_cons = []
    XX_cons, YY_cons, ZZ_cons = [], [], []
    if nodes.lower() in ['y', 'yes']:
        XX, YY, ZZ = [], [], []
        for nod in ops.getNodeTags():
            xyz = ops.nodeCoord(nod)
            if len(xyz) == 2:
                xyz.append(0.0)

            plot_node = True
            if len(xlim) != 0:
                for xx in [xyz[0]]:
                    if xx < xlim[0] or xx > xlim[1]:
                        plot_node = False
            if len(ylim) != 0:
                for yy in [xyz[1]]:
                    if yy < ylim[0] or yy > ylim[1]:
                        plot_node = False
            if len(zlim) != 0:
                for zz in [xyz[2]]:
                    if zz < zlim[0] or zz > zlim[1]:
                        plot_node = False

            if plot_node != False:
                XX.append(xyz[0])
                YY.append(xyz[1])
                ZZ.append(xyz[2])
                plotednodes.append(nod)
                if nodetag.lower() in ['y', 'yes']:
                    x, y, z = xyz
                    ax.text(z, x, y, str(nod), None, size=fontsize, horizontalalignment='center')

        if len(XX) != 0:
            ax.scatter(ZZ, XX, YY, color=nodecolor, s=nodesize, alpha=0.7)

        XX_cons, YY_cons, ZZ_cons = XX, YY, ZZ
        plotednodes_cons = plotednodes

    ### Restraints
    if spconst.lower() in ['y', 'yes'] or rigiddiaph.lower() in ['y', 'yes']:
        if nodes.lower() in ['n', 'no']:
            for nod in ops.getNodeTags():
                xyz = ops.nodeCoord(nod)
                if len(xyz) == 2:
                    xyz.append(0.0)

                plot_node = True
                if len(xlim) != 0:
                    for xx in [xyz[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_node = False
                if len(ylim) != 0:
                    for yy in [xyz[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_node = False
                if len(zlim) != 0:
                    for zz in [xyz[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_node = False

                if plot_node != False:
                    XX_cons.append(xyz[0])
                    YY_cons.append(xyz[1])
                    ZZ_cons.append(xyz[2])
                    plotednodes_cons.append(nod)
    if len(plotednodes_cons) != 0:
         modelfile = 'mymodel.txt'
         ops.printModel('-file', modelfile)
         if spconst.lower() in ['y', 'yes']:
             maxDi = max(abs(max(XX_cons) - min(XX_cons)), abs(max(ZZ_cons) - min(ZZ_cons)))
             factor = maxDi / 65
             cnodes = {}
             with open(modelfile) as f:
                 lines = f.readlines()

             for line in lines:
                 line2 = line.split(" ")
                 if line2[0] == 'SP_Constraint:':
                     n = cnodes.get(line2[3])
                     if int(line2[3]) not in plotednodes_cons:
                        continue

                     if n == None:
                         cnodes[line2[3]] = [line2[5]]
                     else:
                         if line2[5] not in n:
                             n.append(line2[5])
                             cnodes[line2[3]] = n

             __plotrestraint(ops, ax, cnodes, factor)

         if rigiddiaph.lower() in ['y', 'yes']:
             rnodes = {}
             with open(modelfile) as f:
                 lines = f.readlines()

             for line in lines:
                 line2 = line.strip().split(" ")
                 if line2[0] == 'Node' and line2[1] == 'Constrained:':
                     n = rnodes.get(line2[5])
                     if int(line2[5]) not in plotednodes_cons:
                         continue

                     if n == None:
                         rnodes[line2[5]] = [line2[2]]
                     else:
                         if line2[2] not in n:
                             n.append(line2[2])
                             rnodes[line2[5]] = n

             __plotrigiddiaph(ops, ax, rnodes)

        ### Plot Elements
    if elements.lower() in ['y', 'yes']:
        Xzero = []
        Yzero = []
        Zzero = []
        Tzero = []
        for ele in ops.getEleTags():
            elenodes = ops.eleNodes(ele)
            if len(elenodes) == 2:
                xyzi = ops.nodeCoord(elenodes[0])
                xyzj = ops.nodeCoord(elenodes[1])
                if len(xyzi) == 2:
                    xyzi.append(0.0)
                    xyzj.append(0.0)

                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyzi[0], xyzj[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyzi[1], xyzj[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyzi[2], xyzj[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele != False:
                    x = [xyzi[0], xyzj[0]]
                    y = [xyzi[1], xyzj[1]]
                    z = [xyzi[2], xyzj[2]]
                    co = 'royalblue'
                    if xyzi[0] == xyzj[0] and xyzi[1] == xyzj[1] and xyzi[2] == xyzj[2]:
                        Xzero.append(x[0])
                        Yzero.append(y[0])
                        Zzero.append(z[0])
                        Tzero.append(ele)
                        continue
                    if eletag.lower() in ['y', 'yes']:
                        xa = np.average([xyzi[0], xyzj[0]])
                        ya = np.average([xyzi[1], xyzj[1]])
                        za = np.average([xyzi[2], xyzj[2]])
                        ax.text(za, xa, ya, str(ele), None, size=fontsize, horizontalalignment='center')

                    ax.plot(z, x, y, lw=linewidth, color=co)

            elif len(elenodes) == 3:

                xyzi = ops.nodeCoord(elenodes[0])
                xyzj = ops.nodeCoord(elenodes[1])
                xyzk = ops.nodeCoord(elenodes[2])

                if len(xyzi) == 2:
                    xyzi.append(0.0)
                    xyzj.append(0.0)
                    xyzk.append(0.0)

                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyzi[0], xyzj[0], xyzk[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyzi[1], xyzj[1], xyzk[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyzi[2], xyzj[2], xyzk[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele != False:
                    co = 'lightskyblue'
                    if fill.lower() in ['n', 'no']:
                        alpha = 0.0

                    p1 = [xyzi[2], xyzi[0], xyzi[1]]
                    p2 = [xyzj[2], xyzj[0], xyzj[1]]
                    p3 = [xyzk[2], xyzk[0], xyzk[1]]

                    MyMath.plot_area(ax, p1, p2, p3, alpha=alpha, linewidth=edgelinewidth, color=co, edgecolor='silver',
                                sha=False)

                    if eletag.lower() in ['y', 'yes']:
                        xa = np.average([xyzi[0], xyzj[0], xyzk[0]])
                        ya = np.average([xyzi[1], xyzj[1], xyzk[1]])
                        za = np.average([xyzi[2], xyzj[2], xyzk[2]])
                        ax.text(za, xa, ya, str(ele), None, size=fontsize, horizontalalignment='center')
            elif len(elenodes) in [4, 9]:
                xyzi = ops.nodeCoord(elenodes[0])
                xyzj = ops.nodeCoord(elenodes[1])
                xyzk = ops.nodeCoord(elenodes[2])
                xyzl = ops.nodeCoord(elenodes[3])
                if len(xyzi) == 2:
                    xyzi.append(0.0)
                    xyzj.append(0.0)
                    xyzk.append(0.0)
                    xyzl.append(0.0)
                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele != False:
                    co = 'lightskyblue'
                    if fill.lower() in ['n', 'no']:
                        alpha = 0.0

                    p1 = [xyzi[2], xyzi[0], xyzi[1]]
                    p2 = [xyzj[2], xyzj[0], xyzj[1]]
                    p3 = [xyzk[2], xyzk[0], xyzk[1]]
                    p4 = [xyzl[2], xyzl[0], xyzl[1]]
                    MyMath.plot_area(ax, p1, p2, p3, p4, alpha=alpha, linewidth=edgelinewidth, color=co, edgecolor='silver',
                                sha=False)

                    if eletag.lower() in ['y', 'yes']:
                        xa = np.average([xyzi[0], xyzj[0], xyzk[0], xyzl[0]])
                        ya = np.average([xyzi[1], xyzj[1], xyzk[1], xyzl[1]])
                        za = np.average([xyzi[2], xyzj[2], xyzk[2], xyzl[2]])
                        ax.text(za, xa, ya, str(ele), None, size=fontsize, horizontalalignment='center')
            elif len(elenodes) == 8:
                xyz1 = ops.nodeCoord(elenodes[0])
                xyz2 = ops.nodeCoord(elenodes[1])
                xyz3 = ops.nodeCoord(elenodes[2])
                xyz4 = ops.nodeCoord(elenodes[3])
                xyz5 = ops.nodeCoord(elenodes[4])
                xyz6 = ops.nodeCoord(elenodes[5])
                xyz7 = ops.nodeCoord(elenodes[6])
                xyz8 = ops.nodeCoord(elenodes[7])
                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyz1[0], xyz2[0], xyz3[0], xyz4[0], xyz5[0], xyz6[0], xyz7[0], xyz8[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyz1[1], xyz2[1], xyz3[1], xyz4[1], xyz5[1], xyz6[1], xyz7[1], xyz8[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyz1[2], xyz2[2], xyz3[2], xyz4[2], xyz5[2], xyz6[2], xyz7[2], xyz8[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele != False:
                    if eletag.lower() in ['y', 'yes']:
                        xa = np.average([xyz1[0], xyz2[0], xyz3[0], xyz4[0], xyz5[0], xyz6[0], xyz7[0], xyz8[0]])
                        ya = np.average([xyz1[1], xyz2[1], xyz3[1], xyz4[1], xyz5[1], xyz6[1], xyz7[1], xyz8[1]])
                        za = np.average([xyz1[2], xyz2[2], xyz3[2], xyz4[2], xyz5[2], xyz6[2], xyz7[2], xyz8[2]])
                        ax.text(za, xa, ya, str(ele), None, size=fontsize, horizontalalignment='center')

                    co = 'lightskyblue'
                    MyMath.plotcube(ax, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, edgelinewidth,co , fill,'silver', alpha=alpha)

            else:
                print('Are not supported')


        # ax.scatter(Zzero, Xzero, Yzero, c='r', s=linewidth * 2, alpha=0.7)
        # Tzero.append(ele)
    # x_min, x_max = ax.get_xlim()
    # y_min, y_max = ax.get_ylim()
    #
    # X = np.linspace(x_min, x_max, 10)
    # Y = np.linspace(y_min, y_max, 10)
    # X, Y = np.meshgrid(X, Y)
    # Z = np.sqrt(X * 0)
    # surf = ax.plot_surface(X, Y, Z, alpha=0.1, linewidth=0.1, linestyle='--', antialiased=False, facecolor='0.9',
    #                        edgecolor='0.87', shade=False)
    # ax.axis('equal')
def __plotrestraint(ops, ax,  cnodes, fac):
    for nod, valls in cnodes.items():
        xyz = ops.nodeCoord(int(nod))
        if len(xyz) == 2:
            xyz.append(0.0)

        dirs = [int(x) for x in valls]
        for dir in dirs:
            if dir == 1:
                x = [xyz[0], xyz[0] - fac, xyz[0] - fac]
                y = [xyz[1], xyz[1] - fac*0.75, xyz[1] + fac*0.75]
                z = [xyz[2], xyz[2], xyz[2]]
                co = 'r'
            elif dir == 2:
                x = [xyz[0], xyz[0] + fac*0.75, xyz[0] - fac*0.75]
                y = [xyz[1], xyz[1] - fac, xyz[1] - fac]
                z = [xyz[2], xyz[2], xyz[2]]
                co = 'g'
            elif dir == 3:
                x = [xyz[0], xyz[0], xyz[0]]
                y = [xyz[1], xyz[1] + fac*0.75, xyz[1] - fac*0.75]
                z = [xyz[2], xyz[2] - fac, xyz[2] - fac]
                co = 'b'
            elif dir == 4:
                x = [xyz[0], xyz[0], xyz[0] - fac, xyz[0] - fac, xyz[0]]
                y = [xyz[1] - fac*1.5, xyz[1] , xyz[1], xyz[1] - fac*1.5, xyz[1] - fac*1.5]
                z = [xyz[2], xyz[2], xyz[2], xyz[2]]
                co = 'r'
            elif dir == 5:
                x = [xyz[0] - fac*1.5, xyz[0] , xyz[0] , xyz[0] - fac*1.5, xyz[0] - fac*1.5]
                y = [xyz[1], xyz[1], xyz[1] - fac, xyz[1] - fac, xyz[1]]
                z = [xyz[2], xyz[2], xyz[2], xyz[2], xyz[2]]
                co = 'g'
            elif dir == 6:
                x = [xyz[0], xyz[0], xyz[0], xyz[0], xyz[0]]
                y = [xyz[1], xyz[1], xyz[1] - fac*1.5, xyz[1] - fac*1.5, xyz[1]]
                z = [xyz[2], xyz[2] - fac, xyz[2] - fac, xyz[2], xyz[2]]
                co = 'b'

            vertices = [list(zip(z, x, y))]
            poly = Poly3DCollection(vertices, alpha=0.5, linewidth=0.0, color=co, edgecolor='silver')
            ax.add_collection3d(poly)

def __plotrigiddiaph(ops, ax, rnodes):
    for rnod, valls in rnodes.items():
        xyzr = ops.nodeCoord(int(rnod))
        if len(xyzr) == 2:
            xyzr.append(0.0)

        xi, yi, zi = xyzr

        for cnode in valls:
            xyzs = ops.nodeCoord(int(cnode))
            if len(xyzs) == 2:
                xyzs.append(0.0)

            xj, yj, zj = xyzs
            x = [xi, xj]
            y = [yi, yj]
            z = [zi, zj]
            ax.plot(z, x, y, lw=0.35, color='0.7', linestyle='dashed')

# def plot_deformedshape(ops, *parts, ax,scale=10, lineelements='y', quadtrielements='y', brickelements='y', linewidth=0.7, edgelinewidth=0.3,
#                  fill='y', xlim=[], ylim=[],zlim=[], alpha=0.9):
#     global _ndm
#     for arg in [fill, lineelements]:
#         if arg not in ['yes', 'y', 'no', 'n']:
#             raise ValueError("name and subdivisions can "
#                              "be \"yes\", \"y\",  \"no\" or \"n\" ")
#
#     if len(xlim) not in [0, 2]:
#         print('xlim must be an empty list(default) or a list with two float number. default will be used ')
#         xlim = []
#
#     if len(zlim) not in [0, 2]:
#         print('zlim must be an empty list(default) or a list with two float number. default will be used ')
#         zlim = []
#
#     if len(ylim) not in [0, 2]:
#         print('ylim must be an empty list(default) or a list with two float number. default will be used ')
#         ylim = []
#
#         ### Plot Elements
#     # if elements.lower() in ['y', 'yes']:
#     for part in parts:
#         for ele in part.getElements().keys():
#             elenodes = ops.eleNodes(ele)
#             if lineelements.lower() in ['y', 'yes']:
#                 if len(elenodes) == 2:
#                     xyzi = ops.nodeCoord(elenodes[0])
#                     xyzj = ops.nodeCoord(elenodes[1])
#                     dispi = ops.nodeDisp(elenodes[0])
#                     dispj = ops.nodeDisp(elenodes[1])
#                     if len(xyzi) == 2:
#                         xyzi.append(0.0)
#                         xyzj.append(0.0)
#                         dispi[2] = 0.0
#                         dispj[2] = 0.0
#
#                     plot_ele = True
#                     if len(xlim) != 0:
#                         for xx in [xyzi[0], xyzj[0]]:
#                             if xx < xlim[0] or xx > xlim[1]:
#                                 plot_ele = False
#                     if len(ylim) != 0:
#                         for yy in [xyzi[1], xyzj[1]]:
#                             if yy < ylim[0] or yy > ylim[1]:
#                                 plot_ele = False
#                     if len(zlim) != 0:
#                         for zz in [xyzi[2], xyzj[2]]:
#                             if zz < zlim[0] or zz > zlim[1]:
#                                 plot_ele = False
#
#                     if plot_ele != False:
#                         x = [xyzi[0] + scale * dispi[0], xyzj[0] + scale * dispj[0]]
#                         y = [xyzi[1] + scale * dispi[1], xyzj[1] + scale * dispj[1]]
#                         z = [xyzi[2] + scale * dispi[2], xyzj[2] + scale * dispj[2]]
#                         co = 'tab:red'
#                         ax.plot(z, x, y, lw=linewidth, color=co)
#
#             if quadtrielements.lower() in ['y', 'yes']:
#                 if len(elenodes) == 3:
#                     xyzi = ops.nodeCoord(elenodes[0])
#                     xyzj = ops.nodeCoord(elenodes[1])
#                     xyzk = ops.nodeCoord(elenodes[2])
#                     dispi = ops.nodeDisp(elenodes[0])
#                     dispj = ops.nodeDisp(elenodes[1])
#                     dispk = ops.nodeDisp(elenodes[2])
#                     if len(xyzi) == 2:
#                         xyzi.append(0.0)
#                         xyzj.append(0.0)
#                         xyzk.append(0.0)
#                         dispi[2] = 0.0
#                         dispj[2] = 0.0
#                         dispk[2] = 0.0
#                     plot_ele = True
#                     if len(xlim) != 0:
#                         for xx in [xyzi[0], xyzj[0], xyzk[0]]:
#                             if xx < xlim[0] or xx > xlim[1]:
#                                 plot_ele = False
#                     if len(ylim) != 0:
#                         for yy in [xyzi[1], xyzj[1], xyzk[1]]:
#                             if yy < ylim[0] or yy > ylim[1]:
#                                 plot_ele = False
#                     if len(zlim) != 0:
#                         for zz in [xyzi[2], xyzj[2], xyzk[2]]:
#                             if zz < zlim[0] or zz > zlim[1]:
#                                 plot_ele = False
#
#                     if plot_ele != False:
#                         co = 'tab:blue'
#                         if fill.lower() in ['y', 'yes']:
#                             x = [xyzi[0] + scale * dispi[0], xyzj[0] + scale * dispj[0], xyzk[0] + scale * dispk[0]]
#                             y = [xyzi[1] + scale * dispi[1], xyzj[1] + scale * dispj[1], xyzk[1] + scale * dispk[1]]
#                             z = [xyzi[2] + scale * dispi[2], xyzj[2] + scale * dispj[2], xyzk[2] + scale * dispk[2]]
#                             vertices = [list(zip(z, x, y))]
#                             poly = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=co,
#                                                     edgecolor='tab:silver')
#                             ax.add_collection3d(poly)
#                         else:
#                             x = [xyzi[0] + scale * dispi[0], xyzj[0] + scale * dispj[0], xyzk[0] + scale * dispk[0],
#                                  xyzi[0] + scale * dispi[0]]
#                             y = [xyzi[1] + scale * dispi[1], xyzj[1] + scale * dispj[1], xyzk[1] + scale * dispk[1],
#                                  xyzi[1] + scale * dispi[1]]
#                             z = [xyzi[2] + scale * dispi[2], xyzj[2] + scale * dispj[2], xyzk[2] + scale * dispk[2],
#                                  xyzi[2] + scale * dispi[2]]
#                             ax.plot(z, x, y, lw=edgelinewidth, color='tab:silver')
#
#                 elif len(elenodes) in [4, 9]:
#                     xyzi = ops.nodeCoord(elenodes[0])
#                     xyzj = ops.nodeCoord(elenodes[1])
#                     xyzk = ops.nodeCoord(elenodes[2])
#                     xyzl = ops.nodeCoord(elenodes[3])
#                     dispi = ops.nodeDisp(elenodes[0])
#                     dispj = ops.nodeDisp(elenodes[1])
#                     dispk = ops.nodeDisp(elenodes[2])
#                     displ = ops.nodeDisp(elenodes[3])
#                     if len(xyzi) == 2:
#                         xyzi.append(0.0)
#                         xyzj.append(0.0)
#                         xyzk.append(0.0)
#                         xyzl.append(0.0)
#                         dispi[2] = 0.0
#                         dispj[2] = 0.0
#                         dispk[2] = 0.0
#                         displ[2] = 0.0
#                     plot_ele = True
#                     if len(xlim) != 0:
#                         for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
#                             if xx < xlim[0] or xx > xlim[1]:
#                                 plot_ele = False
#                     if len(ylim) != 0:
#                         for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
#                             if yy < ylim[0] or yy > ylim[1]:
#                                 plot_ele = False
#                     if len(zlim) != 0:
#                         for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
#                             if zz < zlim[0] or zz > zlim[1]:
#                                 plot_ele = False
#
#                     if plot_ele != False:
#                         co = 'tab:blue'
#                         if fill.lower() in ['y', 'yes']:
#                             x = [xyzi[0] + scale * dispi[0], xyzj[0] + scale * dispj[0], xyzk[0] + scale * dispk[0], xyzl[0] + scale * displ[0]]
#                             y = [xyzi[1] + scale * dispi[1], xyzj[1] + scale * dispj[1], xyzk[1] + scale * dispk[1], xyzl[1] + scale * displ[1]]
#                             z = [xyzi[2] + scale * dispi[2], xyzj[2] + scale * dispj[2], xyzk[2] + scale * dispk[2], xyzl[2] + scale * displ[2]]
#                             vertices = [list(zip(z, x, y))]
#                             poly = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=co, edgecolor='tab:silver')
#                             ax.add_collection3d(poly)
#                         else:
#                             x = [xyzi[0] + scale * dispi[0], xyzj[0] + scale * dispj[0], xyzk[0] + scale * dispk[0],
#                                  xyzl[0] + scale * displ[0], xyzi[0] + scale * dispi[0]]
#                             y = [xyzi[1] + scale * dispi[1], xyzj[1] + scale * dispj[1], xyzk[1] + scale * dispk[1],
#                                  xyzl[1] + scale * displ[1], xyzi[1] + scale * dispi[1]]
#                             z = [xyzi[2] + scale * dispi[2], xyzj[2] + scale * dispj[2], xyzk[2] + scale * dispk[2],
#                                  xyzl[2] + scale * displ[2], xyzi[2] + scale * dispi[2]]
#                             ax.plot(z, x, y, lw=edgelinewidth, color='tab:silver')
#
#             if brickelements.lower() in ['y', 'yes']:
#                 if len(elenodes) == 8:
#                     xyz = []
#                     disp = []
#                     xyz.append(ops.nodeCoord(elenodes[0]))
#                     xyz.append(ops.nodeCoord(elenodes[1]))
#                     xyz.append(ops.nodeCoord(elenodes[2]))
#                     xyz.append(ops.nodeCoord(elenodes[3]))
#                     xyz.append(ops.nodeCoord(elenodes[4]))
#                     xyz.append(ops.nodeCoord(elenodes[5]))
#                     xyz.append(ops.nodeCoord(elenodes[6]))
#                     xyz.append(ops.nodeCoord(elenodes[7]))
#                     disp.append(ops.nodeDisp(elenodes[0]))
#                     disp.append(ops.nodeDisp(elenodes[1]))
#                     disp.append(ops.nodeDisp(elenodes[2]))
#                     disp.append(ops.nodeDisp(elenodes[3]))
#                     disp.append(ops.nodeDisp(elenodes[4]))
#                     disp.append(ops.nodeDisp(elenodes[5]))
#                     disp.append(ops.nodeDisp(elenodes[6]))
#                     disp.append(ops.nodeDisp(elenodes[7]))
#                     XX = []
#                     YY = []
#                     ZZ = []
#                     for cords in xyz:
#                         XX.append(cords[0])
#                         YY.append(cords[1])
#                         ZZ.append(cords[2])
#                     plot_ele = True
#                     if len(xlim) != 0:
#                         for xx in XX:
#                             if xx < xlim[0] or xx > xlim[1]:
#                                 plot_ele = False
#                     if len(ylim) != 0:
#                         for yy in YY:
#                             if yy < ylim[0] or yy > ylim[1]:
#                                 plot_ele = False
#                     if len(zlim) != 0:
#                         for zz in ZZ:
#                             if zz < zlim[0] or zz > zlim[1]:
#                                 plot_ele = False
#
#                     if plot_ele != False:
#                         xyzd = []
#                         for i in range(len(xyz)):
#                             x = xyz[i][0] + scale * disp[i][0]
#                             y = xyz[i][1] + scale * disp[i][1]
#                             z = xyz[i][2] + scale * disp[i][2]
#                             xyzd.append([x, y, z])
#                         co = 'tab:blue'
#                         MyMath.plotcube(ax, xyzd[0], xyzd[1], xyzd[2], xyzd[3], xyzd[4], xyzd[5], xyzd[6], xyzd[7],
#                                         edgelinewidth,co , fill,'tab:silver', alpha=alpha)

def __plot_contour_surf(ax, X, Y, Z, C, alpha, cmap):
    ax.plot_surface(Z, X, Y, rstride=1, cstride=1, linewidth=0.0, facecolors=cmap(C), shade=False, alpha=alpha,
                    antialiased=False)

def __plot_contour_triangle(ax, X, Y, Z, C, alpha, cmap):
    vertices = [list(zip(Z, X, Y))]
    poly = Poly3DCollection(vertices, alpha=alpha, linewidth=0.0, facecolors=cmap(C))
    ax.add_collection3d(poly)

def __plot_contour_line(ax, X, Y, Z, C, linewidth, cmap):
    colors = cmap(C)
    n = len(X) - 1
    for i in range(n):
        XX = [X[i], X[i + 1]]
        YY = [Y[i], Y[i + 1]]
        ZZ = [Z[i], Z[i + 1]]
        ax.plot(ZZ, XX, YY, color=colors[i], linewidth=linewidth)

def plot_contour_node(name_model, name_analysis, step, resp, direction,dir_name='', parts=[], deformed='y', scale=10,
                      lineelements='y', quadtrielements='y', brickelements='y', linewidth=0.7, edgelinewidth=0.3,
                       xlim=[], ylim=[],zlim=[], alpha=0.9, colormap="rainbow", numseg_line=2, numseg_surf=2):

    fill = 'y'
    for arg in [lineelements]:
        if arg not in ['yes', 'y', 'no', 'n']:
            raise ValueError("name and subdivisions can "
                             "be \"yes\", \"y\",  \"no\" or \"n\" ")

    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []

    ### Plot Elements
    fig = plt.figure(dpi=300)
    ax = fig.add_axes((0, 0.16, 1, 0.78), projection='3d')

    file_model = name_model + "\\" + "file_model.pkl"
    fmodel = open(file_model, 'rb')
    model = dill.load(fmodel)
    fmodel.close()

    file_re = name_model + "\\output_" + name_analysis + ".pkl"
    fresps = open(file_re, 'rb')
    resps = dill.load(fresps)
    db = resps[resp]
    data_ = db.loc[step]

    fresps.close()

    _ndm = model.Ndm
    _ndf = model.Ndf

    parts_created = model.CreatedParts
    parts_ = []
    if len(parts) == 0:
        parts_ = parts_created
    else:
        for part_ in parts_created:
            if (part_.Tag in parts) or (part_.Name in parts):
                parts_.append(part_)

    cmap = matplotlib.colormaps[colormap]

    data = []
    for part in parts_:
        for nod in part.getNodes().keys():
            data.append(data_[nod][direction - 1])

    if deformed.lower() in ['y', 'yes']:
        file_re_disp = name_model + "\\output_" + analysis + ".pkl"
        fresps_disp = open(file_re_disp, 'rb')
        resps_disp = dill.load(fresps_disp)
        db_disp = resps_disp['Disp']
        data_disp = db_disp.loc[step]
        fresps_disp.close()
        disps = {}
        for part in parts_:
            for nod in part.getNodes().keys():
                disps[nod] = (data_disp[nod])

    data_min = min(data)
    data_max = max(data)
    if data_min == 0.0 and data_max == 0.0:
        data_max = 10.0
        data_min = -10.0

    for part in parts_:
        nodes_part = part.getNodes()
        for ele,  elenodes in part.getElements().items():
            if lineelements.lower() in ['y', 'yes']:
                if len(elenodes) == 2:
                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    datai = data_[elenodes[0]]
                    dataj = data_[elenodes[1]]
                    if len(xyzi) == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            dispi = disps[elenodes[0]]
                            dispj = disps[elenodes[1]]
                            if len(xyzi) == 2:
                                dispi[2] = 0.0
                                dispj[2] = 0.0
                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]

                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]

                        if isinstance(direction, str):
                            if len(xyzi) == 3:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1], datai[2]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1], dataj[2]]) ** 2))
                            else:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1]]) ** 2))

                            data_el = [magn_1, magn_2]
                        else:
                            data_el = [datai[direction - 1], dataj[direction - 1]]

                        X, Y, Z, C = MyMath.data_contourplot_line(numseg_line, data_max, data_min, p1, p2, data_el)
                        __plot_contour_line(ax, X, Y, Z, C, linewidth, cmap)

            if quadtrielements.lower() in ['y', 'yes']:
                if len(elenodes) == 3:
                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    xyzk = nodes_part[elenodes[2]]
                    datai = data_[elenodes[0]]
                    dataj = data_[elenodes[1]]
                    datak = data_[elenodes[2]]
                    if len(xyzi) == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            dispi = disps[elenodes[0]]
                            dispj = disps[elenodes[1]]
                            dispk = disps[elenodes[2]]
                            if len(xyzi) == 2:
                                dispi[2] = 0.0
                                dispj[2] = 0.0
                                dispk[2] = 0.0

                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]
                            p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1], xyzk[2] + scale * dispk[2]]
                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]
                            p3 = [xyzk[0], xyzk[1], xyzk[2]]

                        if isinstance(direction, str):
                            if len(xyzi) == 3:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1], datai[2]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1], dataj[2]]) ** 2))
                                magn_3 = np.sqrt(np.sum(np.array([datak[0], datak[1], datak[2]]) ** 2))
                            else:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1]]) ** 2))
                                magn_3 = np.sqrt(np.sum(np.array([datak[0], datak[1]]) ** 2))

                            data_el = [magn_1, magn_2, magn_3]
                        else:
                            data_el = [datai[direction - 1], dataj[direction - 1], datak[direction - 1]]

                        if np.remainder(numseg_surf, 2) != 0:
                            numseg_surf = int(numseg_surf + 1)

                        X, Y, Z, C = MyMath.data_contourplot_tri(int(numseg_surf), data_max, data_min, p1, p2, p3, data_el)
                        for i in range(3):
                            X_, Y_, Z_, C_ = X[i], Y[i], Z[i], C[i]
                            __plot_contour_surf(ax, X_, Y_, Z_, C_, alpha, cmap)

                elif len(elenodes) in [4, 9]:
                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    xyzk = nodes_part[elenodes[2]]
                    xyzl = nodes_part[elenodes[3]]
                    datai = data_[elenodes[0]]
                    dataj = data_[elenodes[1]]
                    datak = data_[elenodes[2]]
                    datal = data_[elenodes[3]]
                    if len(xyzi) == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)
                        xyzl.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            dispi = disps[elenodes[0]]
                            dispj = disps[elenodes[1]]
                            dispk = disps[elenodes[2]]
                            displ = disps[elenodes[3]]
                            if len(xyzi) == 2:
                                dispi[2] = 0.0
                                dispj[2] = 0.0
                                dispk[2] = 0.0
                                displ[2] = 0.0

                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1],
                                  xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1],
                                  xyzj[2] + scale * dispj[2]]
                            p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1],
                                  xyzk[2] + scale * dispk[2]]
                            p4 = [xyzl[0] + scale * displ[0], xyzl[1] + scale * displ[1],
                                  xyzl[2] + scale * displ[2]]

                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]
                            p3 = [xyzk[0], xyzk[1], xyzk[2]]
                            p4 = [xyzl[0], xyzl[1], xyzl[2]]

                        if isinstance(direction, str):
                            if len(xyzi) == 3:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1], datai[2]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1], dataj[2]]) ** 2))
                                magn_3 = np.sqrt(np.sum(np.array([datak[0], datak[1], datak[2]]) ** 2))
                                magn_4 = np.sqrt(np.sum(np.array([datal[0], datal[1], datal[2]]) ** 2))
                            else:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1]]) ** 2))
                                magn_3 = np.sqrt(np.sum(np.array([datak[0], datak[1]]) ** 2))
                                magn_4 = np.sqrt(np.sum(np.array([datal[0], datal[1]]) ** 2))

                            data_el = [magn_1, magn_2, magn_3, magn_4]
                        else:
                            data_el = [datai[direction - 1], dataj[direction - 1], datak[direction - 1], datal[direction - 1]]

                        X, Y, Z, C = MyMath.data_contourplot_quad(numseg_surf, data_max, data_min, p1, p2, p3, p4, data_el)
                        __plot_contour_surf(ax, X, Y, Z, C, alpha, cmap)

            # if brickelements.lower() in ['y', 'yes']:
            #     if len(elenodes) == 8:
            #         xyz = []
            #         disp = []
            #         xyz.append(ops.nodeCoord(elenodes[0]))
            #         xyz.append(ops.nodeCoord(elenodes[1]))
            #         xyz.append(ops.nodeCoord(elenodes[2]))
            #         xyz.append(ops.nodeCoord(elenodes[3]))
            #         xyz.append(ops.nodeCoord(elenodes[4]))
            #         xyz.append(ops.nodeCoord(elenodes[5]))
            #         xyz.append(ops.nodeCoord(elenodes[6]))
            #         xyz.append(ops.nodeCoord(elenodes[7]))
            #         disp.append(ops.nodeDisp(elenodes[0]))
            #         disp.append(ops.nodeDisp(elenodes[1]))
            #         disp.append(ops.nodeDisp(elenodes[2]))
            #         disp.append(ops.nodeDisp(elenodes[3]))
            #         disp.append(ops.nodeDisp(elenodes[4]))
            #         disp.append(ops.nodeDisp(elenodes[5]))
            #         disp.append(ops.nodeDisp(elenodes[6]))
            #         disp.append(ops.nodeDisp(elenodes[7]))
            #         XX = []
            #         YY = []
            #         ZZ = []
            #         for cords in xyz:
            #             XX.append(cords[0])
            #             YY.append(cords[1])
            #             ZZ.append(cords[2])
            #         plot_ele = True
            #         if len(xlim) != 0:
            #             for xx in XX:
            #                 if xx < xlim[0] or xx > xlim[1]:
            #                     plot_ele = False
            #         if len(ylim) != 0:
            #             for yy in YY:
            #                 if yy < ylim[0] or yy > ylim[1]:
            #                     plot_ele = False
            #         if len(zlim) != 0:
            #             for zz in ZZ:
            #                 if zz < zlim[0] or zz > zlim[1]:
            #                     plot_ele = False
            #
            #         if plot_ele != False:
            #             xyzd = []
            #             for i in range(len(xyz)):
            #                 x = xyz[i][0] + scale * disp[i][0]
            #                 y = xyz[i][1] + scale * disp[i][1]
            #                 z = xyz[i][2] + scale * disp[i][2]
            #                 xyzd.append([x, y, z])
            #             co = 'tab:blue'
            #             MyMath.plotcube(ax, xyzd[0], xyzd[1], xyzd[2], xyzd[3], xyzd[4], xyzd[5], xyzd[6], xyzd[7],
            #                             edgelinewidth,co , fill,'tab:silver', alpha=alpha)

    cbaxes = fig.add_axes([0.25, 0.12, 0.5, 0.02])
    if len(dir_name) == 0:
        dir_name = str(direction)

    label = 'Madel: ' + name_model + '    Analysis: ' + analysis + \
            '   Step: ' + str(step) + '    Response: ' + resp + '  ' + dir_name
    ax.set_title(label, fontsize=3, loc='center')
    ax.set_facecolor('0.9')
    mappable = cm.ScalarMappable(cmap=cmap)

    color_step = (data_max - data_min) / 10
    mappable.set_array(np.arange(data_min, data_max + color_step, color_step))
    thicks = []
    for num in np.arange(data_min, data_max + color_step, color_step):
        thicks.append(str("{:0.2E}".format(num)))

    cbar = plt.colorbar(mappable, cax=cbaxes, shrink=0.6, aspect=20, ax=ax, location='bottom', drawedges=False)
    cbar.set_ticklabels(thicks)
    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(3)

    cbar.ax.locator_params(nbins=10)
    cbar.outline.set_edgecolor('white')
    cbar.outline.set_linewidth(0.1)

    ax.axis('off')
    ax.axis('equal')

def plot_contour_ele(name_model, analysis, step, resp, direction, extrapolation='y', avaraging='y', dir_name='',
                     parts=[], deformed='y', scale=10,  lineelements='y', quadtrielements='y', brickelements='y',
                     linewidth=0.7, edgelinewidth=0.3, xlim=[], ylim=[],zlim=[], alpha=0.9, colormap="rainbow",
                     numseg_line=2, numseg_surf=2):

    for arg in [lineelements]:
        if arg not in ['yes', 'y', 'no', 'n']:
            raise ValueError("name and subdivisions can "
                             "be \"yes\", \"y\",  \"no\" or \"n\" ")

    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []

    ### Plot Elements
    fig = plt.figure(dpi=300)
    ax = fig.add_axes((0, 0.16, 1, 0.78), projection='3d')

    file_model = name_model + "\\" + "file_model.pkl"
    fmodel = open(file_model, 'rb')
    model = dill.load(fmodel)
    fmodel.close()

    file_re = name_model + "\\output_" + analysis + ".pkl"
    fresps = open(file_re, 'rb')
    resps = dill.load(fresps)
    db = resps[resp]
    data_ = db.loc[step]

    fresps.close()

    _ndm = model.Ndm
    _ndf = model.Ndf

    parts_created = model.CreatedParts
    parts_ = []
    if len(parts) == 0:
        parts_ = parts_created
    else:
        for part_ in parts_created:
            if (part_.Tag in parts) or (part_.Name in parts):
                parts_.append(part_)

    cmap = matplotlib.colormaps[colormap]

    data_nodes = {}
    for part in parts_created:
        for ele, elenodes in part.getElements().items():
            if len(data_[ele]) != 0:
                num_nodes = len(elenodes)
                num_data = int(len(data_[ele]) / num_nodes)
                data_ele = []
                for i in range(num_nodes):
                    if data_nodes.get(elenodes[i]) == None:
                        data_nodes[elenodes[i]] = [data_[ele][direction + i * num_data - 1]]
                    else:
                        data_nodes[elenodes[i]].append(data_[ele][direction + i * num_data - 1])

    data = []
    for key in data_nodes.keys():
        data_nodes[key] = np.mean(data_nodes[key])
        data.append(np.mean(data_nodes[key]))

    if len(data) == 0:
        return

    if deformed.lower() in ['y', 'yes']:
        file_re_disp = name_model + "\\output_" + analysis + ".pkl"
        fresps_disp = open(file_re_disp, 'rb')
        resps_disp = dill.load(fresps_disp)
        db_disp = resps_disp['Disp']
        data_disp = db_disp.loc[step]
        fresps_disp.close()
        disps = {}
        for part in parts_:
            for nod in part.getNodes().keys():
                disps[nod] = (data_disp[nod])

    data_min = min(data)
    data_max = max(data)

    if data_min == 0.0 and data_max == 0.0:
        data_max = 10.0
        data_min = -10.0

    for part in parts_:
        nodes_part = part.getNodes()
        for ele,  elenodes in part.getElements().items():
            if lineelements.lower() in ['y', 'yes']:
                if len(elenodes) == 2:
                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    if len(data_[ele]) != 0:
                        datai = data_nodes[elenodes[0]]
                        dataj = data_nodes[elenodes[1]]

                    if _ndm == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            dispi = disps[elenodes[0]]
                            dispj = disps[elenodes[1]]
                            if _ndm == 2:
                                dispi[2] = 0.0
                                dispj[2] = 0.0
                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]

                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]

                        if len(data_[ele]) == 0:
                            x = [p1[0], p2[0]]
                            y = [p1[1], p2[1]]
                            z = [p1[2], p2[2]]
                            ax.plot(z, x, y, lw=linewidth, color='royalblue')
                            continue

                        X, Y, Z, C = MyMath.data_contourplot_line(numseg_line, data_max, data_min, p1, p2, [datai, dataj])
                        __plot_contour_line(ax, X, Y, Z, C, linewidth, cmap)

            if quadtrielements.lower() in ['y', 'yes']:
                if len(elenodes) == 3:
                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    xyzk = nodes_part[elenodes[2]]
                    if len(data_[ele]) != 0:
                        datai = data_nodes[elenodes[0]]
                        dataj = data_nodes[elenodes[1]]
                        datak= data_nodes[elenodes[2]]

                    if _ndm == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            dispi = disps[elenodes[0]]
                            dispj = disps[elenodes[1]]
                            dispk = disps[elenodes[2]]
                            if _ndm == 2:
                                dispi[2] = 0.0
                                dispj[2] = 0.0
                                dispk[2] = 0.0

                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]
                            p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1], xyzk[2] + scale * dispk[2]]
                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]
                            p3 = [xyzk[0], xyzk[1], xyzk[2]]

                        if len(data_[ele]) == 0:
                            co = 'lightskyblue'
                            MyMath.plot_area(ax, p1, p2, p3, alpha=alpha, linewidth=edgelinewidth, color=co,
                                             edgecolor='silver',
                                             sha=False)
                            continue

                        if np.remainder(numseg_surf, 2) != 0:
                            numseg_surf = int(numseg_surf + 1)

                        X, Y, Z, C = MyMath.data_contourplot_tri(int(numseg_surf), data_max, data_min, p1, p2, p3,
                                                                 [datai, dataj, datak])
                        for i in range(3):
                            X_, Y_, Z_, C_ = X[i], Y[i], Z[i], C[i]
                            __plot_contour_surf(ax, X_, Y_, Z_, C_, alpha, cmap)

                elif len(elenodes) == 4:

                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    xyzk = nodes_part[elenodes[2]]
                    xyzl = nodes_part[elenodes[3]]
                    if len(data_[ele]) != 0:
                        datai = data_nodes[elenodes[0]]
                        dataj = data_nodes[elenodes[1]]
                        datak = data_nodes[elenodes[2]]
                        datal = data_nodes[elenodes[3]]
                    if _ndm == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)
                        xyzl.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            dispi = disps[elenodes[0]]
                            dispj = disps[elenodes[1]]
                            dispk = disps[elenodes[2]]
                            displ = disps[elenodes[3]]
                            if _ndm == 2:
                                dispi[2] = 0.0
                                dispj[2] = 0.0
                                dispk[2] = 0.0
                                displ[2] = 0.0

                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1],
                                  xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1],
                                  xyzj[2] + scale * dispj[2]]
                            p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1],
                                  xyzk[2] + scale * dispk[2]]
                            p4 = [xyzl[0] + scale * displ[0], xyzl[1] + scale * displ[1],
                                  xyzl[2] + scale * displ[2]]

                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]
                            p3 = [xyzk[0], xyzk[1], xyzk[2]]
                            p4 = [xyzl[0], xyzl[1], xyzl[2]]

                        if len(data_[ele]) == 0:
                            co = 'lightskyblue'
                            MyMath.plot_area(ax, p1, p2, p3, p4, alpha=alpha, linewidth=edgelinewidth, color=co,
                                             edgecolor='silver', sha=False)
                            continue

                        X, Y, Z, C = MyMath.data_contourplot_quad(numseg_surf, data_max, data_min, p1, p2, p3, p4,
                                                                  [datai, dataj, datak, datal])
                        __plot_contour_surf(ax, X, Y, Z, C, alpha, cmap)

                elif len(elenodes) == 9:

                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    xyzk = nodes_part[elenodes[2]]
                    xyzl = nodes_part[elenodes[3]]
                    if len(data_[ele]) != 0:
                        datai = data_nodes[elenodes[0]]
                        dataj = data_nodes[elenodes[1]]
                        datak = data_nodes[elenodes[2]]
                        datal = data_nodes[elenodes[3]]
                    if _ndm == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)
                        xyzl.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            dispi = disps[elenodes[0]]
                            dispj = disps[elenodes[1]]
                            dispk = disps[elenodes[2]]
                            displ = disps[elenodes[3]]
                            if _ndm == 2:
                                dispi[2] = 0.0
                                dispj[2] = 0.0
                                dispk[2] = 0.0
                                displ[2] = 0.0

                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1],
                                  xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1],
                                  xyzj[2] + scale * dispj[2]]
                            p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1],
                                  xyzk[2] + scale * dispk[2]]
                            p4 = [xyzl[0] + scale * displ[0], xyzl[1] + scale * displ[1],
                                  xyzl[2] + scale * displ[2]]

                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]
                            p3 = [xyzk[0], xyzk[1], xyzk[2]]
                            p4 = [xyzl[0], xyzl[1], xyzl[2]]

                        if len(data_[ele]) == 0:
                            co = 'lightskyblue'
                            MyMath.plot_area(ax, p1, p2, p3, p4, alpha=alpha, linewidth=edgelinewidth, color=co,
                                             edgecolor='silver', sha=False)
                            continue

                        X, Y, Z, C = MyMath.data_contourplot_quad(numseg_surf, data_max, data_min, p1, p2, p3, p4,
                                                                  [datai, dataj, datak, datal])
                        __plot_contour_surf(ax, X, Y, Z, C, alpha, cmap)

            # if brickelements.lower() in ['y', 'yes']:
            #     if len(elenodes) == 8:
            #         xyz = []
            #         disp = []
            #         xyz.append(ops.nodeCoord(elenodes[0]))
            #         xyz.append(ops.nodeCoord(elenodes[1]))
            #         xyz.append(ops.nodeCoord(elenodes[2]))
            #         xyz.append(ops.nodeCoord(elenodes[3]))
            #         xyz.append(ops.nodeCoord(elenodes[4]))
            #         xyz.append(ops.nodeCoord(elenodes[5]))
            #         xyz.append(ops.nodeCoord(elenodes[6]))
            #         xyz.append(ops.nodeCoord(elenodes[7]))
            #         disp.append(ops.nodeDisp(elenodes[0]))
            #         disp.append(ops.nodeDisp(elenodes[1]))
            #         disp.append(ops.nodeDisp(elenodes[2]))
            #         disp.append(ops.nodeDisp(elenodes[3]))
            #         disp.append(ops.nodeDisp(elenodes[4]))
            #         disp.append(ops.nodeDisp(elenodes[5]))
            #         disp.append(ops.nodeDisp(elenodes[6]))
            #         disp.append(ops.nodeDisp(elenodes[7]))
            #         XX = []
            #         YY = []
            #         ZZ = []
            #         for cords in xyz:
            #             XX.append(cords[0])
            #             YY.append(cords[1])
            #             ZZ.append(cords[2])
            #         plot_ele = True
            #         if len(xlim) != 0:
            #             for xx in XX:
            #                 if xx < xlim[0] or xx > xlim[1]:
            #                     plot_ele = False
            #         if len(ylim) != 0:
            #             for yy in YY:
            #                 if yy < ylim[0] or yy > ylim[1]:
            #                     plot_ele = False
            #         if len(zlim) != 0:
            #             for zz in ZZ:
            #                 if zz < zlim[0] or zz > zlim[1]:
            #                     plot_ele = False
            #
            #         if plot_ele != False:
            #             xyzd = []
            #             for i in range(len(xyz)):
            #                 x = xyz[i][0] + scale * disp[i][0]
            #                 y = xyz[i][1] + scale * disp[i][1]
            #                 z = xyz[i][2] + scale * disp[i][2]
            #                 xyzd.append([x, y, z])
            #             co = 'tab:blue'
            #             MyMath.plotcube(ax, xyzd[0], xyzd[1], xyzd[2], xyzd[3], xyzd[4], xyzd[5], xyzd[6], xyzd[7],
            #                             edgelinewidth,co , fill,'tab:silver', alpha=alpha)


    cbaxes = fig.add_axes([0.25, 0.12, 0.5, 0.02])
    if len(dir_name) == 0:
        dir_name = str(direction)

    label = 'Madel: ' + name_model + '    Analysis: ' + analysis + \
             '   Step: ' + str(step) + '    Response: ' + resp + '  ' + dir_name
    ax.set_title(label, fontsize=3, loc='center')
    # ax.set_facecolor('0.9')
    mappable = cm.ScalarMappable(cmap=cmap)

    color_step = (data_max - data_min) / 10
    mappable.set_array(np.arange(data_min, data_max + color_step, color_step))
    thicks = []
    for num in np.arange(data_min, data_max + color_step, color_step):
        thicks.append(str("{:0.2E}".format(num)))

    cbar = plt.colorbar(mappable,cax = cbaxes, shrink=0.6, aspect=20, ax=ax, location='bottom', drawedges=False)
    cbar.set_ticklabels(thicks)
    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(3)

    cbar.ax.locator_params(nbins=10)
    cbar.outline.set_edgecolor('white')
    cbar.outline.set_linewidth(0.1)

    ax.axis('off')
    ax.axis('equal')

def plot_contour_disp(ops, name_model, *parts, ax, direction, deformed='y', scale=10, lineelements='y', quadtrielements='y', brickelements='y', linewidth=0.7, edgelinewidth=0.3,
                 xlim=[], ylim=[],zlim=[], alpha=0.9, colormap="rainbow", numseg_line=2, numseg_surf=4 ):

    fill = 'y'
    for arg in [lineelements]:
        if arg not in ['yes', 'y', 'no', 'n']:
            raise ValueError("name and subdivisions can "
                             "be \"yes\", \"y\",  \"no\" or \"n\" ")

    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []

    ### Plot Elements

    file_model = name_model + "\\" + "file_model.pkl"
    fmodel = open(file_model, 'rb')
    model = dill.load(fmodel)
    fmodel.close()

    _ndm = model.Ndm

    parts_created = model.CreatedParts
    parts_ = []
    if len(parts) == 0:
        parts_ = parts
    else:
        for part_ in parts_created:
            if (part_.Tag in parts) or (part_.Name in parts):
                parts_.append(part_)

    cmap = matplotlib.colormaps[colormap]
    disps = []
    for part in parts_:
        for nod in part.getNodes().keys():
            if isinstance(direction, str):
                magn = np.sqrt(np.sum(np.array(ops.nodeDisp(nod)) ** 2))
            else:
                magn = ops.nodeDisp(nod)[direction - 1]
            disps.append(magn)

    disp_min = min(disps)
    disp_max = max(disps)

    for part in parts:
        for ele in part.getElements().keys():
            elenodes = ops.eleNodes(ele)
            if lineelements.lower() in ['y', 'yes']:
                if len(elenodes) == 2:
                    xyzi = ops.nodeCoord(elenodes[0])
                    xyzj = ops.nodeCoord(elenodes[1])
                    dispi = ops.nodeDisp(elenodes[0])
                    dispj = ops.nodeDisp(elenodes[1])
                    if len(xyzi) == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        dispi[2] = 0.0
                        dispj[2] = 0.0

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]

                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]

                        if isinstance(direction, str):
                            magn_1 = np.sqrt(np.sum(np.array([dispi[0], dispi[1], dispi[2]]) ** 2))
                            magn_2 = np.sqrt(np.sum(np.array([dispj[0], dispj[1], dispj[2]]) ** 2))

                            data = [magn_1, magn_2]
                        else:
                            data = [dispi[direction - 1], dispj[direction - 1]]

                        X, Y, Z, C = MyMath.data_contourplot_line(numseg_line, disp_max, disp_min, p1, p2, data)
                        __plot_contour_line(ax, X, Y, Z, C, linewidth, cmap)

            if quadtrielements.lower() in ['y', 'yes']:
                if len(elenodes) == 3:
                    xyzi = ops.nodeCoord(elenodes[0])
                    xyzj = ops.nodeCoord(elenodes[1])
                    xyzk = ops.nodeCoord(elenodes[2])
                    dispi = ops.nodeDisp(elenodes[0])
                    dispj = ops.nodeDisp(elenodes[1])
                    dispk = ops.nodeDisp(elenodes[2])
                    if len(xyzi) == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)
                        dispi[2] = 0.0
                        dispj[2] = 0.0
                        dispk[2] = 0.0
                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]
                            p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1], xyzk[2] + scale * dispk[2]]
                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]
                            p3 = [xyzk[0], xyzk[1], xyzk[2]]
                        if isinstance(direction, str):
                            magn_1 = np.sqrt(np.sum(np.array([dispi[0], dispi[1], dispi[2]]) ** 2))
                            magn_2 = np.sqrt(np.sum(np.array([dispj[0], dispj[1], dispj[2]]) ** 2))
                            magn_3 = np.sqrt(np.sum(np.array([dispk[0], dispk[1], dispk[2]]) ** 2))
                            data = [magn_1, magn_2, magn_3]
                        else:
                            data = [dispi[direction - 1], dispj[direction - 1], dispk[direction - 1]]
                        if np.remainder(numseg_surf, 2) != 0:
                            numseg_surf = int(numseg_surf + 1)

                        X, Y, Z, C = MyMath.data_contourplot_tri(int(numseg_surf), disp_max, disp_min, p1, p2, p3, data)
                        for i in range(3):
                            X_, Y_, Z_, C_ = X[i], Y[i], Z[i], C[i]
                            __plot_contour_surf(ax, X_, Y_, Z_, C_, alpha, cmap)

                elif len(elenodes) in [4, 9]:
                    xyzi = ops.nodeCoord(elenodes[0])
                    xyzj = ops.nodeCoord(elenodes[1])
                    xyzk = ops.nodeCoord(elenodes[2])
                    xyzl = ops.nodeCoord(elenodes[3])
                    dispi = ops.nodeDisp(elenodes[0])
                    dispj = ops.nodeDisp(elenodes[1])
                    dispk = ops.nodeDisp(elenodes[2])
                    displ = ops.nodeDisp(elenodes[3])
                    if len(xyzi) == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)
                        xyzl.append(0.0)
                        dispi[2] = 0.0
                        dispj[2] = 0.0
                        dispk[2] = 0.0
                        displ[2] = 0.0
                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        if deformed.lower() in ['y', 'yes']:
                            p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                            p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]
                            p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1], xyzk[2] + scale * dispk[2]]
                            p4 = [xyzl[0] + scale * displ[0], xyzl[1] + scale * displ[1], xyzl[2] + scale * displ[2]]
                        else:
                            p1 = [xyzi[0], xyzi[1], xyzi[2]]
                            p2 = [xyzj[0], xyzj[1], xyzj[2]]
                            p3 = [xyzk[0], xyzk[1], xyzk[2]]
                            p4 = [xyzl[0], xyzl[1], xyzl[2]]
                        if isinstance(direction, str):
                            magn_1 = np.sqrt(np.sum(np.array([dispi[0], dispi[1], dispi[2]]) ** 2))
                            magn_2 = np.sqrt(np.sum(np.array([dispj[0], dispj[1], dispj[2]]) ** 2))
                            magn_3 = np.sqrt(np.sum(np.array([dispk[0], dispk[1], dispk[2]]) ** 2))
                            magn_4 = np.sqrt(np.sum(np.array([displ[0], displ[1], displ[2]]) ** 2))
                            data = [magn_1, magn_2, magn_3, magn_4]
                        else:
                            data = [dispi[direction - 1], dispj[direction - 1], dispk[direction - 1], displ[direction - 1]]

                        X, Y, Z, C = MyMath.data_contourplot_quad(numseg_surf, disp_max, disp_min, p1, p2, p3, p4, data)
                        __plot_contour_surf(ax, X, Y, Z, C, alpha, cmap)

                        # x = [xyzi[0] + scale * dispi[0], xyzj[0] + scale * dispj[0], xyzk[0] + scale * dispk[0],
                        #      xyzl[0] + scale * displ[0], xyzi[0] + scale * dispi[0]]
                        # y = [xyzi[1] + scale * dispi[1], xyzj[1] + scale * dispj[1], xyzk[1] + scale * dispk[1],
                        #      xyzl[1] + scale * displ[1], xyzi[1] + scale * dispi[1]]
                        # z = [xyzi[2] + scale * dispi[2], xyzj[2] + scale * dispj[2], xyzk[2] + scale * dispk[2],
                        #      xyzl[2] + scale * displ[2], xyzi[2] + scale * dispi[2]]
                        # ax.plot(z, x, y, lw=edgelinewidth, color='k')

            if brickelements.lower() in ['y', 'yes']:
                if len(elenodes) == 8:
                    xyz = []
                    disp = []
                    xyz.append(ops.nodeCoord(elenodes[0]))
                    xyz.append(ops.nodeCoord(elenodes[1]))
                    xyz.append(ops.nodeCoord(elenodes[2]))
                    xyz.append(ops.nodeCoord(elenodes[3]))
                    xyz.append(ops.nodeCoord(elenodes[4]))
                    xyz.append(ops.nodeCoord(elenodes[5]))
                    xyz.append(ops.nodeCoord(elenodes[6]))
                    xyz.append(ops.nodeCoord(elenodes[7]))
                    disp.append(ops.nodeDisp(elenodes[0]))
                    disp.append(ops.nodeDisp(elenodes[1]))
                    disp.append(ops.nodeDisp(elenodes[2]))
                    disp.append(ops.nodeDisp(elenodes[3]))
                    disp.append(ops.nodeDisp(elenodes[4]))
                    disp.append(ops.nodeDisp(elenodes[5]))
                    disp.append(ops.nodeDisp(elenodes[6]))
                    disp.append(ops.nodeDisp(elenodes[7]))
                    XX = []
                    YY = []
                    ZZ = []
                    for cords in xyz:
                        XX.append(cords[0])
                        YY.append(cords[1])
                        ZZ.append(cords[2])
                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in XX:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in YY:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in ZZ:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        xyzd = []
                        for i in range(len(xyz)):
                            x = xyz[i][0] + scale * disp[i][0]
                            y = xyz[i][1] + scale * disp[i][1]
                            z = xyz[i][2] + scale * disp[i][2]
                            xyzd.append([x, y, z])
                        co = 'tab:blue'
                        MyMath.plotcube(ax, xyzd[0], xyzd[1], xyzd[2], xyzd[3], xyzd[4], xyzd[5], xyzd[6], xyzd[7],
                                        edgelinewidth,co , fill,'tab:silver', alpha=alpha)

    mappable = cm.ScalarMappable(cmap=cmap)
    step = (disp_max - disp_min) / 10
    mappable.set_array(np.arange(disp_min, disp_max + step, step))

    plt.colorbar(mappable, shrink=0.9, aspect=40, ax=ax, location='left', label='disp')

def __plotdeformed(anname, resp, name_model, modenumber, direction='mag', dir_name='', parts=[], scale=10, lineelements='y',
                   quadtrielements='y', brickelements='y', linewidth=0.7, edgelinewidth=0.3, xlim=[], ylim=[], zlim=[],
                   alpha=0.70, colormap="rainbow", numseg_line=2, numseg_surf=2):
    for arg in [lineelements]:
        if arg not in ['yes', 'y', 'no', 'n']:
            raise ValueError("name and subdivisions can "
                             "be \"yes\", \"y\",  \"no\" or \"n\" ")

    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []

    fig = plt.figure(dpi=300)
    ax = fig.add_axes((0, 0.16, 1, 0.78), projection='3d')

    file_model = name_model + "\\" + "file_model.pkl"
    fmodel = open(file_model, 'rb')
    model = dill.load(fmodel)
    fmodel.close()

    file_re = name_model + '\\' + "output_" + anname + '\\' + resp + ".feather"
    df = pd.read_feather(file_re)
    dff = df.loc[df['mode_number'] == modenumber]

    data_ = dff.to_dict('list')
    data_.pop('mode_number')
    data_.pop('index')
    data_ = {int(k): list(v[0]) for k, v in data_.items()}

    _ndm = model.Ndm
    _ndf = model.Ndf

    parts_created = model.CreatedParts
    parts_ = []
    if len(parts) == 0:
        parts_ = parts_created
    else:
        for part_ in parts_created:
            if (part_.Tag in parts) or (part_.Name in parts):
                parts_.append(part_)

    cmap = matplotlib.colormaps[colormap]

    data = []
    for part in parts_:
        for nod in part.getNodes().keys():
            if direction == 'mag':
                if _ndf == 2:
                    magn = np.sqrt(np.sum(np.array([data_[nod][0], data_[nod][1]]) ** 2))
                else:
                    magn = np.sqrt(np.sum(np.array([data_[nod][0], data_[nod][1], data_[nod][2]]) ** 2))

                data.append(magn)
            else:
                data.append(data_[nod][direction - 1])

    data_min = min(data)
    data_max = max(data)
    disps = data_
    if data_min == 0.0 and data_max == 0.0:
        data_max = 10.0
        data_min = -10.0

    for part in parts_:
        nodes_part = part.getNodes()
        for ele, elenodes in part.getElements().items():
            if lineelements.lower() in ['y', 'yes']:
                if len(elenodes) == 2:
                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    datai = data_[elenodes[0]]
                    dataj = data_[elenodes[1]]
                    if _ndm == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        dispi = disps[elenodes[0]]
                        dispj = disps[elenodes[1]]
                        if _ndm == 2:
                            dispi[2] = 0.0
                            dispj[2] = 0.0
                        p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                        p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]

                        if isinstance(direction, str):
                            if _ndm == 3:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1], datai[2]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1], dataj[2]]) ** 2))
                            else:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1]]) ** 2))

                            data_el = [magn_1, magn_2]
                        else:
                            data_el = [datai[direction - 1], dataj[direction - 1]]

                        X, Y, Z, C = MyMath.data_contourplot_line(numseg_line, data_max, data_min, p1, p2, data_el)
                        __plot_contour_line(ax, X, Y, Z, C, linewidth, cmap)

            if quadtrielements.lower() in ['y', 'yes']:
                if len(elenodes) == 3:
                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    xyzk = nodes_part[elenodes[2]]
                    datai = data_[elenodes[0]]
                    dataj = data_[elenodes[1]]
                    datak = data_[elenodes[2]]
                    if _ndm == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        dispi = disps[elenodes[0]]
                        dispj = disps[elenodes[1]]
                        dispk = disps[elenodes[2]]
                        if _ndm == 2:
                            dispi[2] = 0.0
                            dispj[2] = 0.0
                            dispk[2] = 0.0

                        p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1], xyzi[2] + scale * dispi[2]]
                        p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1], xyzj[2] + scale * dispj[2]]
                        p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1], xyzk[2] + scale * dispk[2]]

                        if isinstance(direction, str):
                            if len(xyzi) == 3:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1], datai[2]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1], dataj[2]]) ** 2))
                                magn_3 = np.sqrt(np.sum(np.array([datak[0], datak[1], datak[2]]) ** 2))
                            else:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1]]) ** 2))
                                magn_3 = np.sqrt(np.sum(np.array([datak[0], datak[1]]) ** 2))

                            data_el = [magn_1, magn_2, magn_3]
                        else:
                            data_el = [datai[direction - 1], dataj[direction - 1], datak[direction - 1]]

                        if np.remainder(numseg_surf, 2) != 0:
                            numseg_surf = int(numseg_surf + 1)

                        X, Y, Z, C = MyMath.data_contourplot_tri(int(numseg_surf), data_max, data_min, p1, p2, p3,
                                                                 data_el)
                        for i in range(3):
                            X_, Y_, Z_, C_ = X[i], Y[i], Z[i], C[i]
                            __plot_contour_surf(ax, X_, Y_, Z_, C_, alpha, cmap)

                elif len(elenodes) in [4, 9]:
                    xyzi = nodes_part[elenodes[0]]
                    xyzj = nodes_part[elenodes[1]]
                    xyzk = nodes_part[elenodes[2]]
                    xyzl = nodes_part[elenodes[3]]
                    datai = data_[elenodes[0]]
                    dataj = data_[elenodes[1]]
                    datak = data_[elenodes[2]]
                    datal = data_[elenodes[3]]
                    if _ndm == 2:
                        xyzi.append(0.0)
                        xyzj.append(0.0)
                        xyzk.append(0.0)
                        xyzl.append(0.0)

                    plot_ele = True
                    if len(xlim) != 0:
                        for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
                            if xx < xlim[0] or xx > xlim[1]:
                                plot_ele = False
                    if len(ylim) != 0:
                        for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
                            if yy < ylim[0] or yy > ylim[1]:
                                plot_ele = False
                    if len(zlim) != 0:
                        for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
                            if zz < zlim[0] or zz > zlim[1]:
                                plot_ele = False

                    if plot_ele != False:
                        dispi = disps[elenodes[0]]
                        dispj = disps[elenodes[1]]
                        dispk = disps[elenodes[2]]
                        displ = disps[elenodes[3]]
                        if _ndm == 2:
                            dispi[2] = 0.0
                            dispj[2] = 0.0
                            dispk[2] = 0.0
                            displ[2] = 0.0

                        p1 = [xyzi[0] + scale * dispi[0], xyzi[1] + scale * dispi[1],
                              xyzi[2] + scale * dispi[2]]
                        p2 = [xyzj[0] + scale * dispj[0], xyzj[1] + scale * dispj[1],
                              xyzj[2] + scale * dispj[2]]
                        p3 = [xyzk[0] + scale * dispk[0], xyzk[1] + scale * dispk[1],
                              xyzk[2] + scale * dispk[2]]
                        p4 = [xyzl[0] + scale * displ[0], xyzl[1] + scale * displ[1],
                              xyzl[2] + scale * displ[2]]

                        if isinstance(direction, str):
                            if _ndm == 3:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1], datai[2]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1], dataj[2]]) ** 2))
                                magn_3 = np.sqrt(np.sum(np.array([datak[0], datak[1], datak[2]]) ** 2))
                                magn_4 = np.sqrt(np.sum(np.array([datal[0], datal[1], datal[2]]) ** 2))
                            else:
                                magn_1 = np.sqrt(np.sum(np.array([datai[0], datai[1]]) ** 2))
                                magn_2 = np.sqrt(np.sum(np.array([dataj[0], dataj[1]]) ** 2))
                                magn_3 = np.sqrt(np.sum(np.array([datak[0], datak[1]]) ** 2))
                                magn_4 = np.sqrt(np.sum(np.array([datal[0], datal[1]]) ** 2))

                            data_el = [magn_1, magn_2, magn_3, magn_4]
                        else:
                            data_el = [datai[direction - 1], dataj[direction - 1], datak[direction - 1],
                                       datal[direction - 1]]

                        X, Y, Z, C = MyMath.data_contourplot_quad(numseg_surf, data_max, data_min, p1, p2, p3, p4,
                                                                  data_el)
                        __plot_contour_surf(ax, X, Y, Z, C, alpha, cmap)

            # if brickelements.lower() in ['y', 'yes']:
            #     if len(elenodes) == 8:
            #         xyz = []
            #         disp = []
            #         xyz.append(ops.nodeCoord(elenodes[0]))
            #         xyz.append(ops.nodeCoord(elenodes[1]))
            #         xyz.append(ops.nodeCoord(elenodes[2]))
            #         xyz.append(ops.nodeCoord(elenodes[3]))
            #         xyz.append(ops.nodeCoord(elenodes[4]))
            #         xyz.append(ops.nodeCoord(elenodes[5]))
            #         xyz.append(ops.nodeCoord(elenodes[6]))
            #         xyz.append(ops.nodeCoord(elenodes[7]))
            #         disp.append(ops.nodeDisp(elenodes[0]))
            #         disp.append(ops.nodeDisp(elenodes[1]))
            #         disp.append(ops.nodeDisp(elenodes[2]))
            #         disp.append(ops.nodeDisp(elenodes[3]))
            #         disp.append(ops.nodeDisp(elenodes[4]))
            #         disp.append(ops.nodeDisp(elenodes[5]))
            #         disp.append(ops.nodeDisp(elenodes[6]))
            #         disp.append(ops.nodeDisp(elenodes[7]))
            #         XX = []
            #         YY = []
            #         ZZ = []
            #         for cords in xyz:
            #             XX.append(cords[0])
            #             YY.append(cords[1])
            #             ZZ.append(cords[2])
            #         plot_ele = True
            #         if len(xlim) != 0:
            #             for xx in XX:
            #                 if xx < xlim[0] or xx > xlim[1]:
            #                     plot_ele = False
            #         if len(ylim) != 0:
            #             for yy in YY:
            #                 if yy < ylim[0] or yy > ylim[1]:
            #                     plot_ele = False
            #         if len(zlim) != 0:
            #             for zz in ZZ:
            #                 if zz < zlim[0] or zz > zlim[1]:
            #                     plot_ele = False
            #
            #         if plot_ele != False:
            #             xyzd = []
            #             for i in range(len(xyz)):
            #                 x = xyz[i][0] + scale * disp[i][0]
            #                 y = xyz[i][1] + scale * disp[i][1]
            #                 z = xyz[i][2] + scale * disp[i][2]
            #                 xyzd.append([x, y, z])
            #             co = 'tab:blue'
            #             MyMath.plotcube(ax, xyzd[0], xyzd[1], xyzd[2], xyzd[3], xyzd[4], xyzd[5], xyzd[6], xyzd[7],
            #                             edgelinewidth,co , fill,'tab:silver', alpha=alpha)

    cbaxes = fig.add_axes([0.25, 0.12, 0.5, 0.02])
    if len(dir_name) == 0:
        dir_name = str(direction)

    if anname.upper() == 'EIGEN':
        str_step ='   Mode Number: '
    else:
        str_step = '   Step: '

    label = 'Madel: ' + name_model + '    Analysis: ' + anname.upper() + \
            str_step + str(modenumber) + '  ' + dir_name

    ax.set_title(label, fontsize=3, loc='center')
    # ax.set_facecolor('0.9')
    mappable = cm.ScalarMappable(cmap=cmap)

    color_step = (data_max - data_min) / 10
    mappable.set_array(np.arange(data_min, data_max + color_step, color_step))
    thicks = []
    for num in np.arange(data_min, data_max + color_step, color_step):
        thicks.append(str("{:0.2E}".format(num)))

    cbar = plt.colorbar(mappable, cax=cbaxes, shrink=0.6, aspect=20, ax=ax, location='bottom', drawedges=False)
    cbar.set_ticklabels(thicks)
    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(3)

    cbar.ax.locator_params(nbins=10)
    cbar.outline.set_edgecolor('white')
    cbar.outline.set_linewidth(0.1)

    ax.axis('off')
    ax.axis('equal')

def plot_modeshape(name_model,name_analysis, modenumber, direction='mag', dir_name='', parts=[], scale=10, lineelements='y',
                   quadtrielements='y', brickelements='y', linewidth=0.7, edgelinewidth=0.3, xlim=[], ylim=[], zlim=[],
                   alpha=0.70, colormap="rainbow", numseg_line=2, numseg_surf=2):
    __plotdeformed(name_analysis, 'eigen', name_model, modenumber, direction=direction, dir_name=dir_name, parts=parts, scale=scale, lineelements=lineelements,
                   quadtrielements=quadtrielements, brickelements=brickelements, linewidth=linewidth, edgelinewidth=edgelinewidth,
                   xlim=xlim, ylim=ylim, zlim=zlim, alpha=alpha, colormap=colormap, numseg_line=numseg_line, numseg_surf=numseg_surf)


def plot_deformedshape(name_model, name_analysis,  step, direction='mag', dir_name='', parts=[], scale=10, lineelements='y',
                   quadtrielements='y', brickelements='y', linewidth=0.7, edgelinewidth=0.3, xlim=[], ylim=[], zlim=[],
                   alpha=0.70, colormap="rainbow", numseg_line=2, numseg_surf=2):

    __plotdeformed(name_analysis, 'Disp', name_model, step, direction=direction, dir_name=dir_name, parts=parts, scale=scale, lineelements=lineelements,
                   quadtrielements=quadtrielements, brickelements=brickelements, linewidth=linewidth, edgelinewidth=edgelinewidth,
                   xlim=xlim, ylim=ylim, zlim=zlim, alpha=alpha, colormap=colormap, numseg_line=numseg_line, numseg_surf=numseg_surf)

def plot_localcoord(ax, component):
    if isinstance(component, Line):
        xyzi, xyzj = component.XYZi, component.XYZj

        prop = component.EleProps
        if prop['eleType'] in ['Truss', 'TrussSection', 'corotTruss', 'corotTrussSection']:
            return
        elif prop['eleType'] in ['twoNodeLink']:
            orient = []
            for val in prop.values():
                if isinstance(val, list):
                    if val[0] == '-orient':
                        orient = val[1]
                        break
            if len(orient) == 0:
                Vx, Vy, Vz = MyMath.localcoord_line(xyzi, xyzj)
            elif len(orient) == 3:
                Vx = np.array(xyzj) - np.array(xyzi)
                Vy = orient
                Vz = np.cross(Vx, Vy)

            elif len(orient) == 6:
                Vx = [orient[0], orient[1], orient[2]]
                Vy = [orient[3], orient[4], orient[5]]
                Vz = np.cross(Vx, Vy)

            Vx = Vx / np.linalg.norm(Vx)
            Vy = Vy / np.linalg.norm(Vy)
            Vz = Vz / np.linalg.norm(Vz)
            lij = np.sqrt((xyzi[0] - xyzj[0]) ** 2 + (xyzi[1] - xyzj[1]) ** 2 + (xyzi[2] - xyzj[2]) ** 2)
            l = lij / 2
            Vx, Vy, Vz = Vx * l, Vy * l, Vz * l

            xm = np.mean([xyzi[0], xyzj[0]])
            ym = np.mean([xyzi[1], xyzj[1]])
            zm = np.mean([xyzi[2], xyzj[2]])

            ax.plot([zm, Vx[2] + zm], [xm, Vx[0] + xm], [ym, Vx[1] + ym], color='r', linewidth=0.5)
            ax.plot([zm, Vy[2] + zm], [xm, Vy[0] + xm], [ym, Vy[1] + ym], color='g', linewidth=0.5)
            ax.plot([zm, Vz[2] + zm], [xm, Vz[0] + xm], [ym, Vz[1] + ym], color='c', linewidth=0.5)

        else:
            vecxz = []
            for val in prop.values():
                if isinstance(val, geomTransf):
                    vecxz = val.Vecxz
                    if len(vecxz) == 0:
                        vecxz = [0, 0, 1]
                    break

            if len(vecxz) == 0:
                return

            Vx = np.array(xyzj) - np.array(xyzi)
            Vy = np.cross(vecxz, Vx)
            Vz = np.cross(Vx, Vy)

            Vx = Vx / np.linalg.norm(Vx)
            Vy = Vy / np.linalg.norm(Vy)
            Vz = Vz / np.linalg.norm(Vz)
            lij = np.sqrt((xyzi[0] - xyzj[0]) ** 2 + (xyzi[1] - xyzj[1]) ** 2 + (xyzi[2] - xyzj[2]) ** 2)
            l = lij / 10
            Vx, Vy, Vz = Vx * l, Vy * l, Vz * l

            xm = np.mean([xyzi[0], xyzj[0]])
            ym = np.mean([xyzi[1], xyzj[1]])
            zm = np.mean([xyzi[2], xyzj[2]])

            ax.plot([zm, Vx[2] + zm], [xm, Vx[0] + xm], [ym, Vx[1] + ym], color='r', linewidth=0.5)
            ax.plot([zm, Vy[2] + zm], [xm, Vy[0] + xm], [ym, Vy[1] + ym], color='g', linewidth=0.5)
            ax.plot([zm, Vz[2] + zm], [xm, Vz[0] + xm], [ym, Vz[1] + ym], color='c', linewidth=0.5)

    elif isinstance(component, Triangle):
        xyzi, xyzj, xyzk = component.XYZi, component.XYZj, component.XYZk

        xm = np.mean([xyzi[0], xyzj[0], xyzk[0]])
        ym = np.mean([xyzi[1], xyzj[1], xyzk[1]])
        zm = np.mean([xyzi[2], xyzj[2], xyzk[2]])

        Vx, Vy, Vz = MyMath.localcoord_tri(xyzi, xyzj, xyzk)
        lik = np.sqrt((xyzi[0] - xyzk[0]) ** 2 + (xyzi[1] - xyzk[1]) ** 2 + (xyzi[2] - xyzk[2]) ** 2)
        lji = np.sqrt((xyzi[0] - xyzj[0]) ** 2 + (xyzi[1] - xyzj[1]) ** 2 + (xyzi[2] - xyzj[2]) ** 2)
        l = max([lik, lji]) / 10
        Vx, Vy, Vz = Vx * l, Vy * l, Vz * l
        ax.plot([zm, Vx[2] + zm], [xm, Vx[0] + xm], [ym, Vx[1] + ym], color='r', linewidth=0.5)
        ax.plot([zm, Vy[2] + zm], [xm, Vy[0] + xm], [ym, Vy[1] + ym], color='g', linewidth=0.5)
        ax.plot([zm, Vz[2] + zm], [xm, Vz[0] + xm], [ym, Vz[1] + ym], color='c', linewidth=0.5)

    elif isinstance(component, Quad):
        xyzi, xyzj, xyzk, xyzl = component.XYZi, component.XYZj, component.XYZk, component.XYZl

        xm = np.mean([xyzi[0], xyzj[0], xyzk[0], xyzl[0]])
        ym = np.mean([xyzi[1], xyzj[1], xyzk[1], xyzl[1]])
        zm = np.mean([xyzi[2], xyzj[2], xyzk[2], xyzl[2]])

        Vx, Vy, Vz = MyMath.localcoord_quad(xyzi, xyzj, xyzk, xyzl)

        lik = np.sqrt((xyzi[0] - xyzk[0]) ** 2 + (xyzi[1] - xyzk[1]) ** 2 + (xyzi[2] - xyzk[2]) ** 2)
        ljl = np.sqrt((xyzl[0] - xyzj[0]) ** 2 + (xyzl[1] - xyzj[1]) ** 2 + (xyzl[2] - xyzj[2]) ** 2)
        l = min([lik, ljl]) / 10
        Vx, Vy, Vz = Vx * l, Vy * l, Vz * l

        ax.plot([zm, Vx[2] + zm], [xm, Vx[0] + xm], [ym, Vx[1] + ym], color='r', linewidth=0.5)
        ax.plot([zm, Vy[2] + zm], [xm, Vy[0] + xm], [ym, Vy[1] + ym], color='g', linewidth=0.5)
        ax.plot([zm, Vz[2] + zm], [xm, Vz[0] + xm], [ym, Vz[1] + ym], color='c', linewidth=0.5)

    elif isinstance(component, Polygon):
        xyz = component.XYZ

        if len(xyz[0]) == 2:
            for i in range(len(xyz)):
                 xyz[i].append(0.0)

        xm, ym, zm  = np.mean(xyz,axis=0)

        Vx, Vy, Vz = MyMath.localcoord_polygon(xyz)
        n = int(len(xyz) / 2)
        l = np.sqrt((xyz[0][0] - xyz[n][0]) ** 2 + (xyz[0][1] - xyz[n][1]) ** 2 + (xyz[0][2] - xyz[n][2]) ** 2)

        l = l / 10
        Vx, Vy, Vz = Vx * l, Vy * l, Vz * l

        ax.plot([zm, Vx[2] + zm], [xm, Vx[0] + xm], [ym, Vx[1] + ym], color='r', linewidth=0.5)
        ax.plot([zm, Vy[2] + zm], [xm, Vy[0] + xm], [ym, Vy[1] + ym], color='g', linewidth=0.5)
        ax.plot([zm, Vz[2] + zm], [xm, Vz[0] + xm], [ym, Vz[1] + ym], color='c', linewidth=0.5)

    elif isinstance(component, Brick):

        xyz1, xyz2, xyz3, xyz4 = component.XYZ1, component.XYZ2, component.XYZ3, component.XYZ4
        xyz5, xyz6, xyz7, xyz8 = component.XYZ5, component.XYZ6, component.XYZ7, component.XYZ8

        XYZ = [xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8]
        if len(XYZ[0]) == 2:
            for i in range(len(XYZ)):
                 XYZ[i].append(0.0)

        xm = np.mean([xyz1[0], xyz2[0], xyz3[0], xyz4[0],xyz5[0], xyz6[0], xyz7[0], xyz8[0]])
        ym = np.mean([xyz1[1], xyz2[1], xyz3[1], xyz4[1],xyz5[1], xyz6[1], xyz7[1], xyz8[1]])
        zm = np.mean([xyz1[2], xyz2[2], xyz3[2], xyz4[2],xyz5[2], xyz6[2], xyz7[2], xyz8[2]])

        Vx, Vy, Vz = np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])
        l17= np.sqrt((xyz1[0] - xyz7[0]) ** 2 + (xyz1[1] - xyz7[1]) ** 2 + (xyz1[2] - xyz7[2]) ** 2)
        l28 = np.sqrt((xyz2[0] - xyz8[0]) ** 2 + (xyz2[1] - xyz8[1]) ** 2 + (xyz2[2] - xyz8[2]) ** 2)
        l = min([l17, l28]) / 10
        Vx, Vy, Vz = Vx * l, Vy * l, Vz * l

        ax.plot([zm, Vx[2] + zm], [xm, Vx[0] + xm], [ym, Vx[1] + ym], color='r', linewidth=0.5)
        ax.plot([zm, Vy[2] + zm], [xm, Vy[0] + xm], [ym, Vy[1] + ym], color='g', linewidth=0.5)
        ax.plot([zm, Vz[2] + zm], [xm, Vz[0] + xm], [ym, Vz[1] + ym], color='c', linewidth=0.5)
        faces = [[1,2,3,4], [2,6,7,3], [6,5,8,7], [5,1,4,8], [6,2,1,5],[8,4,3,7]]
        for face in faces:
            xyzi, xyzj, xyzk, xyzl = XYZ[face[0] - 1], XYZ[face[1] - 1], XYZ[face[2] - 1], XYZ[face[3] - 1]
            xm = np.mean([xyzi[0], xyzj[0], xyzk[0], xyzl[0]])
            ym = np.mean([xyzi[1], xyzj[1], xyzk[1], xyzl[1]])
            zm = np.mean([xyzi[2], xyzj[2], xyzk[2], xyzl[2]])

            Vx, Vy, Vz = MyMath.localcoord_quad(xyzi, xyzj, xyzk, xyzl)

            lik = np.sqrt((xyzi[0] - xyzk[0]) ** 2 + (xyzi[1] - xyzk[1]) ** 2 + (xyzi[2] - xyzk[2]) ** 2)
            ljl = np.sqrt((xyzl[0] - xyzj[0]) ** 2 + (xyzl[1] - xyzj[1]) ** 2 + (xyzl[2] - xyzj[2]) ** 2)
            l = min([lik, ljl]) / 10
            Vx, Vy, Vz = Vx * l, Vy * l, Vz * l

            ax.plot([zm, Vx[2] + zm], [xm, Vx[0] + xm], [ym, Vx[1] + ym], color='r', linewidth=0.5)
            ax.plot([zm, Vy[2] + zm], [xm, Vy[0] + xm], [ym, Vy[1] + ym], color='g', linewidth=0.5)
            ax.plot([zm, Vz[2] + zm], [xm, Vz[0] + xm], [ym, Vz[1] + ym], color='c', linewidth=0.5)

def plot_coordaxis(ax, linewidth=0.2, length=0.0, fontsize=2.0):

    if length <= 0:
        xl = ax.get_xlim()
        yl = ax.get_ylim()
        dx = xl[1] - xl[0]
        dy = yl[1] - yl[0]
        h = min((dx,dy))
        length = h/15

    ax.quiver([0], [0], [0], [0], [2], [0], color='red',length=length, normalize=True, linewidth=linewidth)
    ax.quiver([0], [0], [0], [0], [0], [2], color='g', length=length, normalize=True, linewidth=linewidth)
    ax.quiver([0], [0], [0], [2], [0], [0], color='c',length=length, normalize=True, linewidth=linewidth)
    ax.text(0, 1.05 * length, 0, 'X', None, fontsize=fontsize, color='red',verticalalignment='center')
    ax.text(0, 0, 1.05 * length, 'Y', None, fontsize=fontsize, color='g')
    ax.text(1.05 * length, 0, 0, 'Z', None, fontsize=fontsize, color='c',verticalalignment='center')

def __plot_load(ax, loc, value, scale, color, linewidth):
    xl, yl, zl = loc
    xd, yd, zd = value
    l = np.sqrt(np.sum(np.array(value) ** 2)) * scale
    ax.quiver(zl, xl, yl, zd, xd, yd, color=color, length=l, normalize=True, linewidth=linewidth)
    # ax.text(xl, yl, zl, str(value))
        
def __plot_load_line(ax, xyzi, xyzj, value, scale, color, linewidth):
    x = [xyzi[0], xyzj[0]]
    y = [xyzi[1], xyzj[1]]
    z = [xyzi[2], xyzj[2]]
    dx, dy, dz = np.array(xyzj) - np.array(xyzi)
    xs, ys, zs = xyzi[0] + 0.05 * dx, xyzi[1] + 0.05 * dy , xyzi[2] + 0.05 * dz
    xe, ye, ze = xyzj[0] - 0.05 * dx, xyzj[1] - 0.05 * dy, xyzj[2] - 0.05 * dz
    X, Y, Z = np.linspace(xs, xe, 5), np.linspace(ys, ye, 5), np.linspace(zs, ze, 5)
    for i in range(len(X)):
        __plot_load(ax, [X[i], Y[i], Z[i]], value, scale, color, linewidth)

    # ax.text(np.mean(x), np.mean(y), np.mean(z), str(value))

def __plot_load_pol(ax, XYZs, value, scale, color, linewidth):
    x = np.array(XYZs)[:, 0]
    y = np.array(XYZs)[:, 1]
    z = np.array(XYZs)[:, 2]
    xm, ym, zm = np.mean(x), np.mean(y), np.mean(z)

    __plot_load(ax, [xm, ym, zm], value, scale, color, linewidth)
    for i in range(len(XYZs)):
        p = (np.array(XYZs[i]) + np.array([xm, ym, zm])) / 2
        __plot_load(ax, p, value, scale, color, linewidth)

    # ax.text(np.mean(x), np.mean(y), np.mean(z), str(value))

def __plot_load_comp_point(ax, comp, pattern, scale, color, linewidth):
   # [pattern, value, direction]
    xyzi = comp.XYZ
    for load in comp.Pointload:
        if load[0]['Name'] != pattern['Name']:
            continue

        value = load[1]
        direction = load[2]
        vals = [0, 0, 0]
        vals[direction-1] = value
        __plot_load(ax, [xyzi[0], xyzi[1], xyzi[2]], vals, scale, color, linewidth)

def __plot_load_comp_line(ax, comp, pattern, scale, color, linewidth):
   # [pattern, value, direction, coord]
    xyzi, xyzj = comp.XYZi, comp.XYZj
    for load in comp.Uniload:
        if load[0]['Name'] != pattern['Name']:
            continue

        value = load[1]
        direction = load[2]
        vals = [0, 0, 0]
        vals[direction-1] = value
        if load[3][0] == 'l':
            prop = comp.EleProps
            vecxz = []
            for val in prop.values():
                if isinstance(val, geomTransf):
                    vecxz = val.Vecxz
                    if len(vecxz) == 0:
                        vecxz = [0, 0, 1]
                    break

            Vx = np.array(xyzj) - np.array(xyzi)
            Vy = np.cross(vecxz, Vx)
            Vz = np.cross(Vx, Vy)
            vals= MyMath.Transform_l2g(vals, Vx, Vy, Vz)

        __plot_load_line(ax, xyzi, xyzj, vals, scale, color, linewidth)

def __plot_load_comp_poly(ax, comp, pattern, scale, color, linewidth):
   # [pattern, value, direction, coord]
    if isinstance(comp, Triangle):
        XYZ = [comp.XYZi, comp.XYZj, comp.XYZk]
    elif isinstance(comp, Quad):
        XYZ = [comp.XYZi, comp.XYZj, comp.XYZk, comp.XYZl]
    elif isinstance(comp, Polygon):
        XYZ = comp.XYZ
    else:
        return

    for load in comp.Uniload:
        if load[0]['Name'] != pattern['Name']:
            continue

        value = load[1]
        direction = load[2]
        vals = [0, 0, 0]
        vals[direction-1] = value
        if load[3][0] == 'l':
            if isinstance(comp, Triangle):
                Vx, Vy, Vz = MyMath.localcoord_tri(comp.XYZi, comp.XYZj, comp.XYZk)
            elif isinstance(comp, Quad):
                Vx, Vy, Vz = MyMath.localcoord_quad(comp.XYZi, comp.XYZj, comp.XYZk, comp.XYZl)
            elif isinstance(comp, Polygon):
                Vx, Vy, Vz = MyMath.localcoord_polygon(XYZ)

            vals = MyMath.Transform_l2g(vals, Vx, Vy, Vz)

        __plot_load_pol(ax, XYZ, vals, scale, color, linewidth)

def __plot_load_comp_brick(ax, comp, pattern, scale, color, linewidth):
    # [pattern, face, value, direction, coord]
    # [pattern, value, direction]
    xyz1, xyz2, xyz3, xyz4 = comp.XYZ1, comp.XYZ2, comp.XYZ3, comp.XYZ4
    xyz5, xyz6, xyz7, xyz8 = comp.XYZ5, comp.XYZ6, comp.XYZ7, comp.XYZ8
    XYZ_ = [xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8]
    xm = np.mean([xyz1[0], xyz2[0], xyz3[0], xyz4[0], xyz5[0], xyz6[0], xyz7[0], xyz8[0]])
    ym = np.mean([xyz1[1], xyz2[1], xyz3[1], xyz4[1], xyz5[1], xyz6[1], xyz7[1], xyz8[1]])
    zm = np.mean([xyz1[2], xyz2[2], xyz3[2], xyz4[2], xyz5[2], xyz6[2], xyz7[2], xyz8[2]])

    faces = [[1, 2, 3, 4], [2, 6, 7, 3], [6, 5, 8, 7], [5, 1, 4, 8], [6, 2, 1, 5], [8, 4, 3, 7]]
    # comp.Bodyload
    for load in comp.Bodyload:
        if load[0]['Name'] != pattern['Name']:
            continue
        value = load[1]
        direction = load[2]
        vals = [0, 0, 0]
        vals[direction-1] = value
        __plot_load(ax, [xm, ym, zm], vals, scale, color, linewidth)

    for load in comp.Surfload:
        if load[0]['Name'] != pattern['Name']:
            continue

        face = faces[load[1]-1]
        XYZ = [XYZ_[face[0] - 1], XYZ_[face[1] - 1], XYZ_[face[2] - 1], XYZ_[face[3] - 1]]
        value = load[2]
        direction = load[3]
        vals = [0, 0, 0]
        vals[direction-1] = value
        if load[4][0] == 'l':
            Vx, Vy, Vz = MyMath.localcoord_quad(XYZ[0], XYZ[1], XYZ[2], XYZ[3])

            vals = MyMath.Transform_l2g(vals, Vx, Vy, Vz)

        __plot_load_pol(ax, XYZ, vals, scale, color, linewidth)

def plot_loads(*parts, ax, pattern, scale=1, color ='k' ,xlim=[], ylim=[],zlim=[], linewidth=0.5):
    for part in parts:
        for component in part.Components:
            if isinstance(component, Line):
                xyzi = component.XYZi
                xyzj = component.XYZj
                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyzi[0], xyzj[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyzi[1], xyzj[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyzi[2], xyzj[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele is True:
                     __plot_load_comp_line(ax, component, pattern, scale, color, linewidth)

            elif isinstance(component, Quad):
                xyzi = component.XYZi
                xyzj = component.XYZj
                xyzk = component.XYZk
                xyzl = component.XYZl
                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyzi[0], xyzj[0], xyzk[0], xyzl[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyzi[1], xyzj[1], xyzk[1], xyzl[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyzi[2], xyzj[2], xyzk[2], xyzl[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele is True:
                    __plot_load_comp_poly(ax, component, pattern, scale, color, linewidth)

            elif isinstance(component, Triangle):
                xyzi = component.XYZi
                xyzj = component.XYZj
                xyzk = component.XYZk

                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyzi[0], xyzj[0], xyzk[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyzi[1], xyzj[1], xyzk[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyzi[2], xyzj[2], xyzk[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele is True:
                    __plot_load_comp_poly(ax, component, pattern, scale, color, linewidth)

            elif isinstance(component, Polygon):
                xyz = component.XYZ
                XX = []
                YY = []
                ZZ = []
                for coords in xyz:
                    XX.append(coords[0])
                    YY.append(coords[1])
                    ZZ.append(coords[2])
                plot_ele = True
                if len(xlim) != 0:
                    for xx in XX:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in YY:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in ZZ:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele is True:
                    __plot_load_comp_poly(ax, component, pattern, scale, color, linewidth)

            elif isinstance(component, Brick):
                xyz1 = component.XYZ1
                xyz2 = component.XYZ2
                xyz3 = component.XYZ3
                xyz4 = component.XYZ4
                xyz5 = component.XYZ5
                xyz6 = component.XYZ6
                xyz7 = component.XYZ7
                xyz8 = component.XYZ8

                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyz1[0], xyz2[0], xyz3[0], xyz4[0], xyz5[0], xyz6[0], xyz7[0], xyz8[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyz1[1], xyz2[1], xyz3[1], xyz4[1], xyz5[1], xyz6[1], xyz7[1], xyz8[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyz1[2], xyz2[2], xyz3[2], xyz4[2], xyz5[2], xyz6[2], xyz7[2], xyz8[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele is True:
                    __plot_load_comp_brick(ax, component, pattern, scale, color, linewidth)

            elif isinstance(component, Point):
                xyz = component.XYZ
                plot_ele = True
                if len(xlim) != 0:
                    for xx in [xyz[0]]:
                        if xx < xlim[0] or xx > xlim[1]:
                            plot_ele = False
                if len(ylim) != 0:
                    for yy in [xyz[1]]:
                        if yy < ylim[0] or yy > ylim[1]:
                            plot_ele = False
                if len(zlim) != 0:
                    for zz in [xyz[2]]:
                        if zz < zlim[0] or zz > zlim[1]:
                            plot_ele = False

                if plot_ele is True:
                   __plot_load_comp_point(ax, component, pattern, scale, color, linewidth)


def nodeexist(ops,xyz, benodes=[]):
    global _ndm
    global _tolerance
    if len(benodes) == 0:
        nodes = ops.getNodeTags()
    else:
        nodes = benodes

    if _ndm == 3:
        x, y, z = xyz
    elif _ndm == 2:
        x, y = xyz[0], xyz[1]
        z = 0
    exist = False

    for nod in nodes:
        if _ndm == 3:
            xn, yn, zn = ops.nodeCoord(nod)
        elif _ndm == 2:
            xn, yn = ops.nodeCoord(nod)
            zn = 0

        if (abs(x - xn) + abs(y - yn) + abs(z - zn)) < _tolerance:
            exist = nod
            break
    return exist


def eigen(ops, name, num_Modes, solver='-genBandArpack'):
    print('######################')
    print('### Eigen Analysis ###')
    print('######################')

    global _name

    start_time = datetime.now().replace(microsecond=0)
    print('Start Time: {}'.format(start_time))

    lambdaN = ops.eigen(solver, num_Modes)
    omega = []
    Tn = []
    for i in range(num_Modes):
        lambdaI = lambdaN[i]
        omega.append(pow(lambdaI, 0.5))
        tt = (2 * np.pi) / pow(lambdaI, 0.5)
        Tn.append(tt)
        print('T' + str(i+1) + ' = ' + str(round(tt, 3)) + '     f' + str(i+1) + ' = ' + str(round(1 / tt, 3)))

    nodes_ = [str(x) for x in ops.getNodeTags()]
    cols = ['mode_number']
    cols.extend(nodes_)
    otputs = pd.DataFrame(columns=cols)

    for i in range(num_Modes):
        vectors = []
        for nod in ops.getNodeTags():
            # magn = np.sqrt(np.sum(np.array(ops.nodeEigenvector(nod, i + 1)) ** 2))
            vectors.append(np.array(ops.nodeEigenvector(nod, i + 1)))

        data_ = [i + 1]
        data_.extend(vectors)
        otputs.loc[i + 1] = data_

    print('Analysis successful')

    end_time = datetime.now().replace(microsecond=0)
    print('End Time: {}'.format(end_time))
    print('Duration: {}'.format(end_time - start_time))

    print('Saving Data ...')
    if os.path.exists(_name + "\\output_eigen\\"):
        shutil.rmtree(_name + "\\output_eigen\\")
    os.mkdir(_name + "\\output_eigen\\")

    file_re = _name + "\\output_eigen\\" + name + ".feather"
    db_output = otputs.reset_index()
    db_output.to_feather(file_re, compression='zstd')
    print('Data was saved to ' + file_re)

    return lambdaN, omega, Tn
def plot_protocol(ax, filename_protocole, Dy):
    step = []
    disp = []
    with open(filename_protocole) as f:
        lines = f.readlines()
    for line in lines:
        line2 = line.split("\t")

        step.append(float(line2[0]))
        disp.append(float(line2[1]))

    f.close()

    target = [x * Dy for x in disp]

    ax.plot(step, target)
    ax.set_xlabel('step')
    ax.set_ylabel('D')
    ax.grid('on')

def analyze_push_cyclic(ops, name, analysis_option, filename_protocole, cnodeTag, cdof, Dy, du_min,
                        du_max, resp_nodes=['Disp', 'Reaction'], resp_elements=['force', 'stresses', 'strains'],
                        everynstep=1, numIter = 10, duDiv=2):
    print('#################################')
    print('### Push Over Cyclic Analysis[', name ,']')
    print('#################################')

    start_time = datetime.now().replace(microsecond=0)
    print('Start Time: {}'.format(start_time))

    logfilename = _name + '\\'+ name + '_opslogfile.txt'
    ops.logFile(logfilename, '-noEcho')

    dofs = []
    for i in range(_ndf):
        dofs.append(int(i + 1))

    nodes_ = ops.getNodeTags()
    elements_ = ops.getEleTags()
    otputs = {}

    resp_node_ID = {'Disp': 1, 'Vel': 2, 'Accel': 3, 'IncrDisp': 4, 'IncrDeltaDisp': 5, 'Reaction': 6, 'Unbalance': 7,
                    'RayleighForces': 8}

    cols_nodes = ['step']
    cols_nodes.extend([str(x) for x in nodes_])

    cols_ele = ['step', 'loc']
    cols_ele.extend([str(x) for x in elements_])

    otputs['Disp'] = pd.DataFrame(columns=cols_nodes)

    for re_n in resp_nodes:
        if re_n != 'Disp':
            otputs[re_n] = pd.DataFrame(columns=cols_nodes)

    for re_n in resp_elements:
        otputs[re_n] = pd.DataFrame(columns=cols_ele)

    start_time = datetime.now().replace(microsecond=0)
    print('Start Time: {}'.format(start_time))

    step = []
    disp = []
    with open(filename_protocole) as f:
        lines = f.readlines()
    for line in lines:
        line2 = line.split("\t")

        step.append(float(line2[0]))
        disp.append(float(line2[1]))

    f.close()

    if disp[0] == 0.0 and step[0] == 0:
        disp.pop(0)

    TargetDisp = [x * Dy for x in disp]

    print('# Analysis Option:')
    ops.wipeAnalysis()
    print('ops.wipeAnalysis()')
    for key, vals in analysis_option.items():
        str_opt = 'ops.' + key + '('
        for i in range(len(vals)-1):
            val = vals[i]
            if isinstance(val, str):
                str_opt = str_opt + "\'" + val + "\'" + ', '
            else:
                str_opt = str_opt + str(val) + ', '
        val = vals[-1]
        if isinstance(val, str):
            str_opt = str_opt + "\'" + val + "\'" + ')'
        else:
            str_opt = str_opt + str(val) + ')'

        print(str_opt)
        eval(str_opt)

    print('# Start Analysis: ')
    node_location = 0
    Nstep = 1
    savedstep = 1
    for i in range(len(TargetDisp)):
        print('Step ' + str(i + 1) + '/' + str(len(TargetDisp)) + ':')
        if TargetDisp[i] > node_location:
            du = du_max
        else:
            du = du_max * -1

        if abs(TargetDisp[i] - node_location) < abs(du):
            du = TargetDisp[i] - node_location

        print('    Try du = ', str(du))
        ops.integrator('DisplacementControl', cnodeTag, cdof, du, numIter)
        ops.analysis('Static')

        num_suc = 0
        while round(abs(node_location - TargetDisp[i]), 7) > 0:
            du_end = TargetDisp[i] - node_location
            if abs(du_end) < abs(du):
                du = du_end
                print('    Try du = ', str(du))
                ops.integrator('DisplacementControl', cnodeTag, cdof, du, numIter)
                num_suc = 0

            if num_suc == 10:
                if abs(du * duDiv) <= du_max:
                    du = du * duDiv
                    if abs(du_end) < abs(du):
                        du = du_end

                    ops.integrator('DisplacementControl', cnodeTag, cdof, du, numIter)
                    print('    Try du = ', str(du))
                    num_suc = 0

            ok = ops.analyze(1)
            if ok != 0:
                num_suc = 0
                print('    Analysis failed at step ', str(Nstep))
                du = du / duDiv
                if abs(du) < du_min:
                    print('  Analysis failed: du < dumin =  ', str (du_min), '     Loc = ', str(round(node_location, 7))
                          , '    Target = ', str(TargetDisp[i]))
                    end_time = datetime.now().replace(microsecond=0)

                    print('End Time: {}'.format(end_time))
                    print('Duration: {}'.format(end_time - start_time))

                    print('Saving Data ...')
                    if os.path.exists(_name + "\\output_" + name + "\\"):
                        shutil.rmtree(_name + "\\output_" + name + "\\")
                    os.mkdir(_name + "\\output_" + name + "\\")

                    for ou in otputs.keys():
                        file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
                        db_output = otputs[ou].reset_index()
                        db_output.to_feather(file_re, compression='zstd')

                    print('Data was saved to ' + _name + "\\output_" + name)
                    exit()
                print('    Try du = ', str(du))
                ops.integrator('DisplacementControl', cnodeTag, cdof, du, numIter)
            else:
                if (Nstep == savedstep) or (node_location + du == TargetDisp[-1]):
                    for re_n in resp_elements:
                        data_ele = [Nstep, node_location + du]
                        data_ele.extend([ops.eleResponse(n, re_n) for n in elements_])
                        otputs[re_n].loc[Nstep] = data_ele

                    for re_n in resp_nodes:
                        resp_s = []
                        for n in nodes_:
                            resp = []
                            for dof in dofs:
                                resp.append(ops.nodeResponse(n, dof, resp_node_ID[re_n]))

                            resp_s.append(resp)

                        data_node = [Nstep, node_location + du]
                        data_node.extend(resp_s)
                        otputs[re_n].loc[Nstep] = data_node

                    savedstep += everynstep
                node_location += du
                print('    Analysis successful at step ', str(Nstep), '     Loc = ', str(round(node_location, 7)),
                          '    Target = ', str(TargetDisp[i]))
                Nstep += 1
                num_suc += 1

    print('Analysis successful')

    end_time = datetime.now().replace(microsecond=0)
    print('End Time: {}'.format(end_time))
    print('Duration: {}'.format(end_time - start_time))

    print('Saving Data ...')
    if os.path.exists(_name + "\\output_" + name + "\\"):
        shutil.rmtree(_name + "\\output_" + name + "\\")
    os.mkdir(_name + "\\output_" + name + "\\")

    for ou in otputs.keys():
        file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
        db_output = otputs[ou].reset_index()
        db_output.to_feather(file_re, compression='zstd')

    print('Data was saved to ' + _name + "\\output_" + name)

def analyze_static(ops,name, analysis_option, num_steps=10, resp_nodes=[],
                   resp_elements=[], everynstep=1, loadConst='yes', time=0.0):
    print('##########################')
    print('### Static Analysis[', name ,']')
    print('##########################')

    global _name
    global _ndf
    global _parts
    logfilename = _name + '\\'+ name + '_opslogfile.txt'
    ops.logFile(logfilename, '-noEcho')

    dofs = []
    for i in range(_ndf):
        dofs.append(int(i + 1))

    nodes_ = ops.getNodeTags()
    elements_ = ops.getEleTags()
    otputs = {}

    resp_node_ID = {'Disp': 1, 'Vel': 2, 'Accel': 3, 'IncrDisp': 4, 'IncrDeltaDisp': 5, 'Reaction': 6, 'Unbalance': 7,
                    'RayleighForces': 8}

    cols_nodes = ['step']
    cols_nodes.extend([str(x) for x in nodes_])

    cols_ele = ['step']
    cols_ele.extend([str(x) for x in elements_])

    otputs['Disp'] = pd.DataFrame(columns=cols_nodes)

    for re_n in resp_nodes:
        if re_n != 'Disp':
            otputs[re_n] = pd.DataFrame(columns=cols_nodes)

    for re_n in resp_elements:
        otputs[re_n] = pd.DataFrame(columns=cols_ele)

    start_time = datetime.now().replace(microsecond=0)
    print('Start Time: {}'.format(start_time))

    ops.record()

    print('# Analysis Option:')
    ops.wipeAnalysis()
    print('ops.wipeAnalysis()')
    for key, vals in analysis_option.items():
        str_opt = 'ops.' + key + '('
        for i in range(len(vals) - 1):
            val = vals[i]
            if isinstance(val, str):
                str_opt = str_opt + "\'" + val + "\'" + ', '
            else:
                str_opt = str_opt + str(val) + ', '
        val = vals[-1]
        if isinstance(val, str):
            str_opt = str_opt + "\'" + val + "\'" + ')'
        else:
            str_opt = str_opt + str(val) + ')'

        print(str_opt)
        eval(str_opt)
    print("ops.integrator(\'LoadControl\', " + str(1 / num_steps) + ")")
    print("ops.analysis(\'Static\')")

    ops.integrator('LoadControl', 1 / num_steps)
    ops.analysis('Static')

    print('# Start Analysis: ')

    savedstep = 1

    num_steps = int(num_steps)
    for step in range(num_steps):
        ok = ops.analyze(1)
        if ok != 0:
            print('    Analysis failed at step ' + str(step + 1) + '/' + str(num_steps))
            end_time = datetime.now().replace(microsecond=0)
            print('End Time: {}'.format(end_time))
            print('Duration: {}'.format(end_time - start_time))

            print('Saving Data ...')
            if os.path.exists(_name + "\\output_" + name + "\\"):
                shutil.rmtree(_name + "\\output_" + name + "\\")
            os.mkdir(_name + "\\output_" + name + "\\")

            for ou in otputs.keys():
                file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
                db_output = otputs[ou].reset_index()
                db_output.to_feather(file_re, compression='zstd')

            print('Data was saved to ' + _name + "\\output_" + name)
            exit()
        else:
            if step == savedstep or (step == num_steps):
                for re_n in resp_elements:
                    data_ele = [step]
                    data_ele.extend([ops.eleResponse(n, re_n) for n in elements_])
                    otputs[re_n].loc[step] = data_ele

                for re_n in resp_nodes:
                    resp_s = []
                    for n in nodes_:
                        resp = []
                        for dof in dofs:
                            resp.append(ops.nodeResponse(n, dof, resp_node_ID[re_n]))

                        resp_s.append(resp)

                    data_node = [step]
                    data_node.extend(resp_s)
                    otputs[re_n].loc[step] = data_node

                savedstep += everynstep

        print('    Analysis successful at step ' + str(step + 1) + '/' + str(num_steps))

    if loadConst.lower() in ['y', 'yes']:
         ops.loadConst('-time', time)

    ops.remove('recorders')

    print('Analysis successful')

    end_time = datetime.now().replace(microsecond=0)
    print('End Time: {}'.format(end_time))
    print('Duration: {}'.format(end_time - start_time))

    print('Saving Data ...')
    if os.path.exists(_name + "\\output_" + name + "\\"):
        shutil.rmtree(_name + "\\output_" + name + "\\")
    os.mkdir(_name + "\\output_" + name + "\\")

    for ou in otputs.keys():
        file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
        db_output = otputs[ou].reset_index()
        db_output.to_feather(file_re, compression='zstd')

    print('Data was saved to ' + _name + "\\output_" + name)

def analyze_push_mono(ops, name, analysis_option, TargetDisp, cnodeTag, cdof, du_min, du_max,
                      resp_nodes=[], resp_elements=[], everynstep=1,
                      numIter=10, duDiv=2):

    print('####################################')
    print('### Push Over Monotonic Analysis[', name,']')
    print('####################################')
    global _name
    global _ndf
    global _parts

    start_time = datetime.now().replace(microsecond=0)
    print('Start Time: {}'.format(start_time))

    logfilename = _name + '\\'+ name + '_opslogfile.txt'
    ops.logFile(logfilename, '-noEcho')

    dofs = []
    for i in range(_ndf):
        dofs.append(int(i + 1))

    nodes_ = ops.getNodeTags()
    elements_ = ops.getEleTags()
    otputs = {}

    resp_node_ID = {'Disp': 1, 'Vel': 2, 'Accel': 3, 'IncrDisp': 4, 'IncrDeltaDisp': 5, 'Reaction': 6, 'Unbalance': 7,
                    'RayleighForces': 8}

    cols_nodes = ['step', 'loc']
    cols_nodes.extend([str(x) for x in nodes_])

    cols_ele = ['step', 'loc']
    cols_ele.extend([str(x) for x in elements_])

    otputs['Disp'] = pd.DataFrame(columns=cols_nodes)

    for re_n in resp_nodes:
        if re_n != 'Disp':
            otputs[re_n] = pd.DataFrame(columns=cols_nodes)

    for re_n in resp_elements:
        otputs[re_n] = pd.DataFrame(columns=cols_ele)

    print('# Analysis Option:')
    ops.wipeAnalysis()
    print('ops.wipeAnalysis()')
    for key, vals in analysis_option.items():
        str_opt = 'ops.' + key + '('
        for i in range(len(vals) - 1):
            val = vals[i]
            if isinstance(val, str):
                str_opt = str_opt + "\'" + val + "\'" + ', '
            else:
                str_opt = str_opt + str(val) + ', '
        val = vals[-1]
        if isinstance(val, str):
            str_opt = str_opt + "\'" + val + "\'" + ')'
        else:
            str_opt = str_opt + str(val) + ')'

        print(str_opt)
        eval(str_opt)
    print('# Start Analysis: ')

    Nstep = 1
    savedstep = 1
    node_location = 0

    if TargetDisp > node_location:
        du = du_max
    else:
        du = du_max * -1
    print('    du = ', str(du))

    ops.integrator('DisplacementControl', cnodeTag, cdof, du, numIter)
    ops.analysis('Static')

    num_suc = 0
    while round(abs(node_location - TargetDisp), 7) > 0:
        if abs(TargetDisp - node_location) < abs(du):
            du = TargetDisp - node_location
            print('    Try du = ', str(du))
            ops.integrator('DisplacementControl', cnodeTag, cdof, du, numIter)
            num_suc = 0

        if num_suc == 10:
            if abs(du * duDiv) <= du_max:
                du = du * duDiv
                ops.integrator('DisplacementControl', cnodeTag, cdof, du, numIter)
                print('    Try du = ', str(du))
                num_suc = 0

        ok = ops.analyze(1)
        if ok != 0:
            num_suc = 0
            print('    Analysis failed at step ', str(Nstep))
            du = du / duDiv
            if abs(du) < du_min:
                print('  Analysis failed: du < dumin ', '     Loc = ', str(round(node_location, 7)),
                      '    Target = ', str(TargetDisp))

                end_time = datetime.now().replace(microsecond=0)
                print('End Time: {}'.format(end_time))
                print('Duration: {}'.format(end_time - start_time))

                print('Saving Data ...')
                if os.path.exists(_name + "\\output_" + name + "\\"):
                    shutil.rmtree(_name + "\\output_" + name + "\\")
                os.mkdir(_name + "\\output_" + name + "\\")

                for ou in otputs.keys():
                    file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
                    db_output = otputs[ou].reset_index()
                    db_output.to_feather(file_re, compression='zstd')

                print('Data was saved to ' + _name + "\\output_" + name)

                # import opsvis
                # opsvis.plot_defo(3, az_el=(90, -90))
                # plt.show()
                exit()

            print('    Try du = ', str(du))
            ops.integrator('DisplacementControl', cnodeTag, cdof, du, numIter)
        else:
            if (Nstep == savedstep) or (node_location + du == TargetDisp):
                for re_n in resp_elements:
                    data_ele = [Nstep, node_location + du]
                    data_ele.extend([ops.eleResponse(n, re_n) for n in elements_])
                    otputs[re_n].loc[Nstep] = data_ele

                for re_n in resp_nodes:
                    resp_s = []
                    for n in nodes_:
                        resp = []
                        for dof in dofs:
                            resp.append(ops.nodeResponse(n, dof, resp_node_ID[re_n]))

                        resp_s.append(resp)

                    data_node = [Nstep, node_location + du]
                    data_node.extend(resp_s)
                    otputs[re_n].loc[Nstep] = data_node

                savedstep += everynstep

            node_location += du
            print('    Analysis successful at step ', str(Nstep), '     Loc = ',
                  str(round(node_location, 7)), '    Target = ', str(TargetDisp))
            Nstep += 1
            num_suc += 1

    print('Analysis successful')

    end_time = datetime.now().replace(microsecond=0)
    print('End Time: {}'.format(end_time))
    print('Duration: {}'.format(end_time - start_time))

    print('Saving Data ...')
    if os.path.exists(_name + "\\output_" + name + "\\"):
        shutil.rmtree(_name + "\\output_" + name + "\\")
    os.mkdir(_name + "\\output_" + name + "\\")

    for ou in otputs.keys():
        file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
        db_output = otputs[ou].reset_index()
        db_output.to_feather(file_re, compression='zstd')

    print('Data was saved to ' + _name + "\\output_" + name)

def plot_record(ax, filename_record, factor=1, xtitle='time(s)', ytitle='acceleration(g)', title=''):
    time = []
    acceleration = []
    with open(filename_record) as f:
        lines = f.readlines()
    for line in lines:
        line2 = line.split("\t")

        time.append(float(line2[0]))
        acceleration.append(float(line2[1]) * factor)

    f.close()

    ax.plot(time, acceleration, linewidth=0.5)
    ax.set_xlabel(xtitle)
    ax.set_ylabel(ytitle)
    ax.set_title(title)
    ax.grid('on')

def analyze_transient(ops, name, analysis_option, filename_record, tag_timeseries, factor, tag_pattern, direction=1, dt_min=0,
                      dt_max=0, dt_Div=2, resp_nodes=['Disp', 'Reaction'], resp_elements=['force', 'stresses', 'strains'],
                      everynstep=1, saveatsteps='n', type='-accel'):
    global _name
    global _ndf
    otputs = {}
    try:
        print('##########################')
        print('### Transient Analysis[', name ,']')
        print('##########################')

        start_time = datetime.now().replace(microsecond=0)
        print('Start Time: {}'.format(start_time))
        logfilename = _name + '\\'+ name + '_opslogfile.txt'
        ops.logFile(logfilename, '-noEcho')

        dofs = []
        for i in range(_ndf):
            dofs.append(int(i + 1))

        nodes_ = ops.getNodeTags()
        elements_ = ops.getEleTags()

        resp_node_ID = {'Disp': 1, 'Vel': 2, 'Accel': 3, 'IncrDisp': 4, 'IncrDeltaDisp': 5, 'Reaction': 6, 'Unbalance': 7,
                        'RayleighForces': 8}

        cols_nodes = ['step', 'time']
        cols_nodes.extend([str(x) for x in nodes_])

        cols_ele = ['step', 'time']
        cols_ele.extend([str(x) for x in elements_])

        otputs['Disp'] = pd.DataFrame(columns=cols_nodes)

        for re_n in resp_nodes:
            if re_n != 'Disp':
                otputs[re_n] = pd.DataFrame(columns=cols_nodes)

        for re_n in resp_elements:
            otputs[re_n] = pd.DataFrame(columns=cols_ele)

        time = []
        acceleration = []
        with open(filename_record) as f:
            lines = f.readlines()
        for line in lines:
            line2 = line.split("\t")
            time.append(float(line2[0]))
            acceleration.append(float(line2[1]))

        f.close()

        _dt = time[1] - time[0]

        filename_temp = '__'+ filename_record
        if os.path.exists(filename_temp):
            os.remove(filename_temp)

        with open(filename_temp, 'w') as f:
            for acc in acceleration:
                f.write(f"{acc}\n")

        # Set time series to be passed to uniform excitation
        str_timeSeries = "ops.timeSeries(\'Path\'," + ' ' + str(tag_timeseries) + ", \'-filePath\' ,\'" + filename_temp + \
                         "', \'-dt\', " + str(_dt) + ", \'-factor\', " + str(factor) + ")"

        print(str_timeSeries)
        eval(str_timeSeries)
        # ops.timeSeries('Path', tag_timeseries, '-filePath', filename_temp, '-dt', _dt, '-factor', factor)

        # Create UniformExcitation load pattern
        #                         tag dir
        # ops.pattern('UniformExcitation',  tag_pattern,  direction,  type, tag_timeseries)
        str_pattern = "ops.pattern(\'UniformExcitation\', " + str(tag_pattern) + ', ' + str(direction) + ', \'' + type + \
                      '\', ' + str(tag_timeseries) + ')'
        print(str_pattern)
        eval(str_pattern)

        print('# Analysis Option:')
        ops.wipeAnalysis()
        print('ops.wipeAnalysis()')
        for key, vals in analysis_option.items():
            str_opt = 'ops.' + key + '('
            for i in range(len(vals)-1):
                val = vals[i]
                if isinstance(val, str):
                    str_opt = str_opt + "\'" + val + "\'" + ', '
                else:
                    str_opt = str_opt + str(val) + ', '
            val = vals[-1]
            if isinstance(val, str):
                str_opt = str_opt + "\'" + val + "\'" + ')'
            else:
                str_opt = str_opt + str(val) + ')'

            print(str_opt)
            eval(str_opt)

        print('# Start Analysis: ')

        if dt_max <= 0:
            print('### dt_max <= 0.0, dt_max was set to dt = ' + str(_dt))
            dt_max = _dt

        if dt_max > _dt:
            print("Warning: ")
            print('### dt_max = ' + str(dt_max) + '   dt = ' + str(_dt) + '  dt_max > dt')

        if dt_min <= 0:
            print('### dt_min <= 0.0, dt_min was set to dt_max / 10')
            dt_min = dt_max / 10

        if dt_min > _dt:
            print('### dt_min >  dt, dt_min was set to dt_max / 10')
            dt_min = dt_max / 10

        if dt_min > dt_max:
            print('### dt_min >  dt_max, dt_min was set to dt_max / 10')
            dt_min = dt_max / 10

        print('    dt = ', str(dt_max))
        dt = dt_max
        ops.analysis('Transient')

        Nstep = 1
        savedstep = 1
        time_final = time[-1]
        time_cur = 0
        num_suc = 0

        while round(time_final - time_cur, 7) > 0:
            dt_end = time_final - time_cur
            if dt_end < dt:
                dt = dt_end
                print('    Try dt = ', str(dt))
                num_suc = 0

            if num_suc == 20:
                if dt * dt_Div <= dt_max:
                    dt = dt * dt_Div
                    if dt_end < dt:
                        dt = dt_end

                    print('    Try dt = ', str(dt))
                    num_suc = 0

            ok = ops.analyze(1, dt)
            if ok != 0:
                print('    Analysis failed at step ', str(Nstep), '   time = ', str(round(time_cur, 4)) , '/',
                      str(round(time_final, 4)), '   ', str(round(100 * time_cur/ time_final, 2)),'%')
                dt = dt / dt_Div
                if abs(dt) < dt_min:
                    print('  Analysis failed: dt < dtmin ', '   time = ', str(round(time_cur, 4)) , '/',
                      str(round(time_final, 4)), '   ', str(round(100 * time_cur/ time_final, 2)),'%')
                    end_time = datetime.now().replace(microsecond=0)
                    print('End Time: {}'.format(end_time))
                    print('Duration: {}'.format(end_time - start_time))

                    print('Saving Data ...')
                    if os.path.exists(_name + "\\output_" + name + "\\"):
                        shutil.rmtree(_name + "\\output_" + name + "\\")
                    os.mkdir(_name + "\\output_" + name + "\\")

                    for ou in otputs.keys():
                        file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
                        db_output = otputs[ou].reset_index()
                        db_output.to_feather(file_re, compression='zstd')

                    print('Data was saved to ' + _name + "\\output_" + name)
                    exit()

                print('    Try dt = ', str(dt))
                num_suc = 0
            else:
                if (Nstep == savedstep) or (time_cur + dt == time_final):
                    for re_n in resp_elements:
                        data_ele = [Nstep, time_cur + dt]
                        data_ele.extend([ops.eleResponse(n, re_n) for n in elements_])
                        otputs[re_n].loc[Nstep] = data_ele

                    for re_n in resp_nodes:
                        resp_s = []
                        for n in nodes_:
                            resp = []
                            for dof in dofs:
                                resp.append(ops.nodeResponse(n, dof, resp_node_ID[re_n]))

                            resp_s.append(resp)

                        data_node = [Nstep, time_cur + dt]
                        data_node.extend(resp_s)
                        otputs[re_n].loc[Nstep] = data_node

                    savedstep += everynstep

                    if saveatsteps.lower() in ['y', 'yes']:
                        if os.path.exists(_name + "\\output_" + name + "\\"):
                            shutil.rmtree(_name + "\\output_" + name + "\\")
                        os.mkdir(_name + "\\output_" + name + "\\")

                        for ou in otputs.keys():
                            file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
                            db_output = otputs[ou].reset_index()
                            db_output.to_feather(file_re, compression='zstd')

                time_cur += dt
                print('    Analysis successful at step ', str(Nstep), '   time = ', str(round(time_cur, 4)) , '/',
                      str(round(time_final, 4)), '   ', str(round(100 * time_cur/ time_final, 2)),'%')
                Nstep += 1
                num_suc += 1

        print('Analysis successful')

        end_time = datetime.now().replace(microsecond=0)
        print('End Time: {}'.format(end_time))
        print('Duration: {}'.format(end_time - start_time))

        print('Saving Data ...')
        if os.path.exists(_name + "\\output_" + name + "\\"):
            shutil.rmtree(_name + "\\output_" + name + "\\")
        os.mkdir(_name + "\\output_" + name + "\\")

        for ou in otputs.keys():
            file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
            db_output = otputs[ou].reset_index()
            db_output.to_feather(file_re, compression='zstd')

        print('Data was saved to ' + _name + "\\output_" + name)

    except:
        print('Saving Data ...')
        if os.path.exists(_name + "\\output_" + name + "\\"):
            shutil.rmtree(_name + "\\output_" + name + "\\")
        os.mkdir(_name + "\\output_" + name + "\\")

        for ou in otputs.keys():
            file_re = _name + "\\output_" + name + "\\" + ou + ".feather"
            db_output = otputs[ou].reset_index()
            db_output.to_feather(file_re, compression='zstd')

        print('Data was saved to ' + _name + "\\output_" + name)

def damping(ops, xDamp, T1=0, T2=0, factor_betaK = 0.0, factor_betaKinit= 0.0, factor_betaKcomm= 1.0,
            xlim=[], ylim=[], zlim=[], solver='-genBandArpack'):

    if T1 == 0 or T2 == 0:
        lambdaN, omega, Tn = eigen(ops, 2, solver=solver)
        omegaI, omegaJ = omega
    else:
        omegaI, omegaJ = (2 * np.pi) / T1, (2 * np.pi) / T2
        lambdaN = [omegaI ** 2, omegaJ ** 2]
        Tn = [T1, T2]
        omega = [omegaI, omegaJ]

    alphaM = xDamp * (2 * omegaI * omegaJ) / (omegaI + omegaJ)
    betaSt = 2 * (xDamp / (omegaI + omegaJ))

    if len(xlim) == 0 and len(ylim) == 0 and len(zlim) == 0:
        ops.rayleigh(alphaM, factor_betaK * betaSt, factor_betaKinit * betaSt, factor_betaKcomm * betaSt)
    else:
        dnodes = find_nodes(ops, xlim, ylim, zlim)
        if dnodes is False:
            return

        delements = findelements(ops, xlim, ylim, zlim)
        if delements is False:
            return

        ops.region(1, '-ele', *delements, '-rayleigh', 0.0, factor_betaK * betaSt,
                   factor_betaKinit * betaSt, factor_betaKcomm * betaSt)
        ops.region(2, '-node', *dnodes, '-rayleigh', alphaM, 0.0, 0.0, 0.0)

    return alphaM, betaSt, lambdaN, omega, Tn

def find_node(ops, xyz):
    global _ndm
    global _tolerance
    nodes = ops.getNodeTags()
    if _ndm == 3:
        x, y, z = xyz
    elif _ndm == 2:
        x, y = xyz[0], xyz[1]
        z = 0

    nodeTags = []
    for nod in nodes:
        if _ndm == 3:
            xn, yn, zn = ops.nodeCoord(nod)
        elif _ndm == 2:
            xn, yn = ops.nodeCoord(nod)
            zn = 0

        if (abs(x - xn) + abs(y - yn) + abs(z - zn)) < _tolerance:
            nodeTags.append(nod)
    if len(nodeTags) == 0:
        return False
    elif len(nodeTags) == 1:
        return nodeTags[0]
    else:
        return nodeTags

def find_nodes_dict(benodes, xlim=[], ylim=[], zlim=[]):
    global _ndm
    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []

    nodeTags = []
    for nod in benodes.keys():
        xyz = benodes[nod]
        if _ndm == 2:
            xyz.append(0.0)

        add_node = True
        if len(xlim) != 0:
            for xx in [xyz[0]]:
                if xx < xlim[0] or xx > xlim[1]:
                    add_node = False
        if len(ylim) != 0:
            for yy in [xyz[1]]:
                if yy < ylim[0] or yy > ylim[1]:
                    add_node = False
        if len(zlim) != 0:
            for zz in [xyz[2]]:
                if zz < zlim[0] or zz > zlim[1]:
                    add_node = False

        if add_node != False:
            nodeTags.append(nod)

    if len(nodeTags) == 0:
            return False
    else:
        return nodeTags


def find_nodes(ops, xlim=[], ylim=[], zlim=[]):
    global _ndm
    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []

    nodeTags = []
    for nod in ops.getNodeTags():
        xyz = ops.nodeCoord(nod)
        if _ndm == 2:
            xyz.append(0.0)

        add_node = True
        if len(xlim) != 0:
            for xx in [xyz[0]]:
                if xx < xlim[0] or xx > xlim[1]:
                    add_node = False
        if len(ylim) != 0:
            for yy in [xyz[1]]:
                if yy < ylim[0] or yy > ylim[1]:
                    add_node = False
        if len(zlim) != 0:
            for zz in [xyz[2]]:
                if zz < zlim[0] or zz > zlim[1]:
                    add_node = False

        if add_node != False:
            nodeTags.append(nod)

    if len(nodeTags) == 0:
            return False
    else:
        return nodeTags


def findelements(ops, xlim=[], ylim=[], zlim=[]):
    if len(xlim) not in [0, 2]:
        print('xlim must be an empty list(default) or a list with two float number. default will be used ')
        xlim = []

    if len(zlim) not in [0, 2]:
        print('zlim must be an empty list(default) or a list with two float number. default will be used ')
        zlim = []

    if len(ylim) not in [0, 2]:
        print('ylim must be an empty list(default) or a list with two float number. default will be used ')
        ylim = []

    eleTags = []
    for ele in ops.getEleTags():
        elenodes = ops.eleNodes(ele)
        XX = []
        YY = []
        ZZ = []
        for nod in elenodes:
            xyz = ops.nodeCoord(nod)
            XX.append(xyz[0])
            YY.append(xyz[1])
            if _ndm == 2:
                ZZ.append(0.0)
            else:
                ZZ.append(xyz[2])

        add_ele = True
        if len(xlim) != 0:
            for xx in [XX]:
                if xx < xlim[0] or xx > xlim[1]:
                    add_ele = False
        if len(ylim) != 0:
            for yy in [YY]:
                if yy < ylim[0] or yy > ylim[1]:
                    add_ele = False
        if len(zlim) != 0:
            for zz in [ZZ]:
                if zz < zlim[0] or zz > zlim[1]:
                    add_ele = False

        if add_ele != False:
            eleTags.append(ele)

    if len(eleTags) == 0:
        return False
    else:
        return eleTags


def converttoline(xyz, length, dir, lineprop, numDiv=1, number=1):
    global _ndm
    name = 'line'
    if _ndm == 2:
        ux, uy, uz = dir[0], dir[1], 0
        lu = np.sqrt(ux ** 2 + uy ** 2 + uz ** 2)
        ux, uy, uz = ux * length / lu, uy * length / lu, uz * length / lu
        x, y, z = xyz[0], xyz[1], 0
    else:
        ux, uy, uz = dir
        lu = np.sqrt(ux ** 2 + uy ** 2 + uz ** 2)
        ux, uy, uz = ux * length / lu, uy * length / lu, uz * length / lu
        x, y, z = xyz

    lines = []
    for n in range(number):
        lname = name + "_" + str(n+1)
        xyzi = [x + n * ux, y + n * uy, z + n * uz]
        xyzj = [x + (n + 1) * ux, y + (n + 1) * uy, z + (n + 1) * uz]
        lines.append(Line(lname, lineprop, xyzi, xyzj, numDiv))

    return lines

def converttoquad(line, length, dir, quadprop, numDivij=1, numDivjk=1, number=1):
    global _ndm
    name = 'quad'
    xyzi_l = line.XYZi
    xyzj_l = line.XYZj
    if _ndm == 2:
        ux, uy, uz = dir[0], dir[1], 0
        lu = np.sqrt(ux ** 2 + uy ** 2 + uz ** 2)
        ux, uy, uz = ux * length / lu, uy * length / lu, uz * length / lu
        xi_l, yi_l, zi_l = xyzi_l[0], xyzi_l[1], 0
        xj_l, yj_l, zj_l = xyzj_l[0], xyzj_l[1], 0
    else:
        ux, uy, uz = dir
        lu = np.sqrt(ux ** 2 + uy ** 2 + uz ** 2)
        ux, uy, uz = ux * length / lu, uy * length / lu, uz * length / lu
        xi_l, yi_l, zi_l = xyzi_l
        xj_l, yj_l, zj_l = xyzj_l
    quads = []
    for n in range(number):
        qname = name + "_" + str(n+1)
        xyzi = [xi_l + n * ux, yi_l + n * uy, zi_l + n * uz]
        xyzj = [xi_l + (n + 1) * ux, yi_l + (n + 1) * uy, zi_l + (n + 1) * uz]
        xyzk = [xj_l + (n + 1) * ux, yj_l + (n + 1) * uy, zj_l + (n + 1) * uz]
        xyzl = [xj_l + n * ux, yj_l + n * uy, zj_l + n * uz]

        quads.append(Quad(qname, quadprop, xyzi, xyzj, xyzk, xyzl,
             Nij=numDivij, Njk=numDivjk))

    return quads

def propcommand(eletag,nodes,eleprops):
    strcommand = 'element('
    args = list(eleprops.keys())
    eletype = eleprops[args[0]]
    str_nodes = ""
    for n in nodes:
        str_nodes = str_nodes + str(n) + ", "

    str_params = ''
    for i in range(3, len(args)):
        if type(eleprops[args[i]]) == list:
            if type(eleprops[args[i]][0]) == str and eleprops[args[i]][0][0] == "-":
                paramname = eleprops[args[i]][0]
                str_param_ = "'" + paramname + "', "
                paramvals = eleprops[args[i]][1]
                if type(paramvals) == list:
                    for val in paramvals:
                        if type(val) == str:
                            str_param_ = str_param_ + "'" + val + "', "
                        else:
                            str_param_ = str_param_ + str(val) + ", "
                else:
                    if type(paramvals) == str:
                        str_param_ = str_param_ + "'" + paramvals + "', "
                    else:
                        str_param_ = str_param_ + str(paramvals) + ", "

            else:
                str_param_ = ""
                paramvals = eleprops[args[i]]
                for val in paramvals:
                    if type(val) == str:
                        str_param_ = str_param_ + "'" + val + "', "
                    else:
                        str_param_ = str_param_ + str(val) + ", "
        elif isinstance(eleprops[args[i]], geomTransf):
            str_param_ = str(eleprops[args[i]].Tag) + ", "

        else:
            if type(eleprops[args[i]]) == str:
                str_param_ = "'" + str(eleprops[args[i]]) + "', "
            else:
                str_param_ = str(eleprops[args[i]]) + ", "

        str_params = str_params + str_param_

    strcommand = strcommand + "'" + eletype + "', " + str(eletag) + ", " + str_nodes + str_params
    strcommand = strcommand.strip()

    if strcommand[-1] == ",":
        strcommand = ")".join(strcommand.rsplit(strcommand[-1:], 1))
    else:
        strcommand = strcommand + ")"

    return strcommand

def find_nodepairs(ops,masternodes,slavenodes):
    global _tolerance
    pairs = {}
    for n in masternodes:
        pairs[n] = []
        xyz = ops.nodeCoord(n)
        if len(xyz) == 2:
            xyz.append(0.0)
        x, y, z = xyz
        for s in slavenodes:
            xyz = ops.nodeCoord(s)
            if len(xyz) == 2:
                xyz.append(0.0)
            xs, ys, zs = xyz
            if (abs(x - xs) + abs(y - ys) + abs(z - zs)) < _tolerance:
                val = pairs[n]
                val.append(s)

    up_pairs = {key: val for key, val in pairs.items() if val != []}
    return up_pairs

def add_zerolength(ops,masternodes,slavenodes,zerprop,print_command='y'):
    global _name
    zelements = {}
    masternodes = list(masternodes)
    slavenodes = list(slavenodes)
    if len(ops.getEleTags()) == 0:
        eleTag = 0
    else:
        eleTag = int(np.max(ops.getEleTags()))
    elecount = 1
    nodepairs = find_nodepairs(ops, masternodes, slavenodes)
    file_elements = open(_name + "\\" + "file_elements.txt", "a")
    for mnode in nodepairs.keys():
        snodes = nodepairs[mnode]
        for snode in snodes:
            if mnode != snode:
                str_elecommand = propcommand(elecount + eleTag, [mnode, snode], zerprop)
                str_command = "ops." + str_elecommand

                file_elements.write(str_command + '\n')
                zelements[elecount + eleTag] = [mnode, snode]

                if print_command.lower() in ['y', 'yes']:
                    print(str_command)

                eval(str_command)

                # elements_[ele + eleTag] = nodes
                elecount += 1

    file_elements.close()
    return zelements

def readrecord(filename, sum_=False, startcolumn=2, factor=1.0):
    x = filename.rfind(".")
    sheatname = filename[:x]
    filename_excel = sheatname + '.xlsx'
    datalist = []
    with open(filename) as f:
        lines = f.readlines()
        count = 1
    for line in lines:
        line2 = line.split(" ")
        data_row = [float(x) for x in line2]
        data_row.insert(0, count)
        count += 1
        if sum_:
            s = sum(data_row[startcolumn:]) * factor
            data_row.append(s)

        datalist.append(data_row)

    f.close()
    dfd = pd.DataFrame(datalist)
    with pd.ExcelWriter(filename_excel) as writer:
        dfd.to_excel(writer, sheet_name=sheatname, index=False, header=False)
    return np.array(datalist)

class MyMath:
        @staticmethod
        def localcoord_polygon(xyz):
            if len(xyz) == 3:
                Vx, Vy, Vz = MyMath.localcoord_tri(xyz[0], xyz[1], xyz[2])
            else:
                xyzi, xyzj, xyzk, xyzl = xyz[0], xyz[1], xyz[-2], xyz[-1]
                Vx, Vy, Vz = MyMath.localcoord_quad(xyzi, xyzj, xyzk, xyzl)

            return Vx, Vy, Vz

        def localcoord_quad(xyzi, xyzj, xyzk, xyzl):
            global _tolerance
            V1 = np.array(xyzj) - np.array(xyzi)
            V2 = np.array(xyzl) - np.array(xyzi)
            Vz = np.cross(V1, V2)
            Vz = Vz / np.linalg.norm(Vz)

            Vx = [1, 0, 0]
            Vy = np.cross(Vz, Vx)
            if abs(abs(np.dot(Vz, [0, 1, 0])) - 1.0) > _tolerance:
                Vx = np.cross([0, 1, 0], Vz)

            Vy = np.cross(Vz, Vx)
            Vx = Vx / np.linalg.norm(Vx)
            Vy = Vy / np.linalg.norm(Vy)

            return Vx, Vy, Vz

        @staticmethod
        def localcoord_tri(xyzi, xyzj, xyzk):
            global _tolerance
            V1 = np.array(xyzj) - np.array(xyzi)
            V2 = np.array(xyzk) - np.array(xyzi)
            Vz = np.cross(V1, V2)
            Vz = Vz / np.linalg.norm(Vz)

            Vx = [1, 0, 0]
            Vy = np.cross(Vz, Vx)
            if abs(abs(np.dot(Vz, [0, 1, 0])) - 1.0) > _tolerance:
                Vx = np.cross([0, 1, 0], Vz)

            Vy = np.cross(Vz, Vx)
            Vx = Vx / np.linalg.norm(Vx)
            Vy = Vy / np.linalg.norm(Vy)

            return Vx, Vy, Vz

        @staticmethod
        def localcoord_line(xyzi, xyzj):
            global _tolerance
            Vx = np.array(xyzj) - np.array(xyzi)
            Vz = [0, 0, 1]
            if abs(abs(np.dot(Vx, [0, 1, 0])) - 1.0) > _tolerance:
                Vz = np.cross(Vx, [0, 1, 0])

            Vy = np.cross(Vz, Vx)
            Vx = Vx / np.linalg.norm(Vx)
            Vy = Vy / np.linalg.norm(Vy)
            Vz = Vz / np.linalg.norm(Vz)
            return Vx, Vy, Vz

        @staticmethod
        def divideline(xyzi, xyzj, N, staruum):
            xi, yi, zi = xyzi
            xj, yj, zj = xyzj
            XX = np.linspace(xi, xj, num=N + 1)
            YY = np.linspace(yi, yj, num=N + 1)
            ZZ = np.linspace(zi, zj, num=N + 1)
            numbering = np.linspace(staruum, staruum + N, num=N + 1, dtype=int)
            return XX, YY, ZZ, numbering

        @staticmethod
        def dividecube(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, N12, N14, N15):
            x1, y1, z1 = xyz1
            x2, y2, z2 = xyz2
            x3, y3, z3 = xyz3
            x4, y4, z4 = xyz4

            x5, y5, z5 = xyz5
            x6, y6, z6 = xyz6
            x7, y7, z7 = xyz7
            x8, y8, z8 = xyz8

            xrow15 = np.linspace(x1, x5, num=N15 + 1)
            yrow15 = np.linspace(y1, y5, num=N15 + 1)
            zrow15 = np.linspace(z1, z5, num=N15 + 1)

            xrow26 = np.linspace(x2, x6, num=N15 + 1)
            yrow26 = np.linspace(y2, y6, num=N15 + 1)
            zrow26 = np.linspace(z2, z6, num=N15 + 1)

            xrow37 = np.linspace(x3, x7, num=N15 + 1)
            yrow37 = np.linspace(y3, y7, num=N15 + 1)
            zrow37 = np.linspace(z3, z7, num=N15 + 1)

            xrow48 = np.linspace(x4, x8, num=N15 + 1)
            yrow48 = np.linspace(y4, y8, num=N15 + 1)
            zrow48 = np.linspace(z4, z8, num=N15 + 1)
            coords = []
            Noderange = []
            Nodes = {}
            for i in range(N15 + 1):
                nodenum = (N14 + 1) * (N12 + 1) * i
                xyz15 = [xrow15[i], yrow15[i], zrow15[i]]
                xyz26 = [xrow26[i], yrow26[i], zrow26[i]]
                xyz37 = [xrow37[i], yrow37[i], zrow37[i]]
                xyz48 = [xrow48[i], yrow48[i], zrow48[i]]
                coords_pl, Noderange_pl, nnodes = MyMath.dividequad(xyz15, xyz26, xyz37, xyz48, N12, N14, nodenum)
                for n in nnodes:
                    Nodes[n[0]] = [n[1], n[2], n[3]]
                coords.append(coords_pl)
                Noderange.append(Noderange_pl)

            return coords, np.array(Noderange), Nodes


        @staticmethod
        def dividequad(xyz1, xyz2, xyz3, xyz4, N12, N14, nodenum):
            x1, y1, z1 = xyz1
            x2, y2, z2 = xyz2
            x3, y3, z3 = xyz3
            x4, y4, z4 = xyz4
            coords = {}

            XX = np.zeros((N14 + 1, N12 + 1))
            YY = np.zeros((N14 + 1, N12 + 1))
            ZZ = np.zeros((N14 + 1, N12 + 1))
            Noderange = np.zeros((N14 + 1, N12 + 1))

            Xst = np.linspace(x1, x4, num=N14 + 1)
            Xen = np.linspace(x2, x3, num=N14 + 1)

            Yst = np.linspace(y1, y4, num=N14 + 1)
            Yen = np.linspace(y2, y3, num=N14 + 1)

            Zst = np.linspace(z1, z4, num=N14 + 1)
            Zen = np.linspace(z2, z3, num=N14 + 1)
            nodes = []
            for i in range(0, N14 + 1):
                xrow = np.linspace(Xst[i], Xen[i], num=N12 + 1)
                yrow = np.linspace(Yst[i], Yen[i], num=N12 + 1)
                zrow = np.linspace(Zst[i], Zen[i], num=N12 + 1)
                nraw = np.linspace(i * (N12 + 1) + 1, i * (N12 + 1) + 1 + N12, num=N12 + 1)
                nrawn = [int(x + nodenum) for x in nraw]
                for k in range(len(xrow)):
                    nodes.append([nrawn[k], xrow[k], yrow[k], zrow[k]])

                XX[i, :] = xrow
                YY[i, :] = yrow
                ZZ[i, :] = zrow
                Noderange[i, :] = nrawn
                for j in range(N12 + 1):
                    coords[nrawn[j]] = [xrow[j], yrow[j], zrow[j]]

            return coords, Noderange, nodes

        @staticmethod
        def extractbricknodesets(Noderange):
            # 12
            nodeset_12 = Noderange[0, 0, 0:]

            # 23
            nodeset_23 = Noderange[0, 0:, -1]

            # 43
            nodeset_43 = Noderange[0, -1, 0:]

            # 14
            nodeset_14 = Noderange[0, 0:, 0]

            # 15
            nodeset_15 = Noderange[0:, 0, 0]

            # 26
            nodeset_26 = Noderange[0:, 0, -1]

            # 37
            nodeset_37 = Noderange[0:, -1, -1]

            # 48
            nodeset_48 = Noderange[0:, -1, 0]
            # print(nodeset_48)

            # 56
            nodeset_56 = Noderange[-1, 0, 0:]

            # 67
            nodeset_67 = Noderange[-1, 0:, -1]

            # 87
            nodeset_87 = Noderange[-1, -1, 0:]

            # 58
            nodeset_58 = Noderange[-1, 0:, 0]

            nodeste = {1: {'Nodes': Noderange[0],
                           'ij': nodeset_12,
                           'jk': nodeset_23,
                           'kl': np.flip(nodeset_43),
                           'li': np.flip(nodeset_14)
                           },
                       2: {'Nodes': np.transpose(Noderange[0:, 0:, -1]),
                           'ij': nodeset_26,
                           'jk': nodeset_67,
                           'kl': np.flip(nodeset_37),
                           'li': np.flip(nodeset_23)
                           },
                       3: {'Nodes': Noderange[-1],
                           'ij': np.flip(nodeset_56),
                           'jk': nodeset_58,
                           'kl': nodeset_87,
                           'li': np.flip(nodeset_67)
                           },
                       4: {'Nodes': np.transpose(Noderange[0:, 0:, 0]),
                           'ij': np.flip(nodeset_15),
                           'jk': nodeset_14,
                           'kl': nodeset_48,
                           'li': np.flip(nodeset_58)

                           },
                       5: {'Nodes': Noderange[0:, 0, 0:],
                           'ij': np.flip(nodeset_12),
                           'jk': nodeset_15,
                           'kl': nodeset_56,
                           'li': np.flip(nodeset_26)

                           },
                       6: {'Nodes': Noderange[0:, -1, 0:],
                           'ij': nodeset_43,
                           'jk': nodeset_37,
                           'kl': np.flip(nodeset_87),
                           'li': np.flip(nodeset_48)

                           }
                       }

            return nodeste

        @staticmethod
        def extractbrickelements(coords, N12, N14):
            elements = {}
            elecount = 1
            for i in range(len(coords) - 1):
                pl1 = coords[i]
                pl2 = coords[i + 1]
                nodenum1 = (N14 + 1) * (N12 + 1) * i
                nodenum2 = (N14 + 1) * (N12 + 1) * (i + 1)
                for j in range(1, N14 + 1):
                    for k in range(1, N12 + 1):
                        nodes = {}
                        n1 = k + (j - 1) * (N12 + 1)
                        n2 = n1 + 1
                        n3 = n2 + N12 + 1
                        n4 = n1 + N12 + 1

                        nodes[n1 + nodenum1] = pl1[n1 + nodenum1]
                        nodes[n2 + nodenum1] = pl1[n2 + nodenum1]
                        nodes[n3 + nodenum1] = pl1[n3 + nodenum1]
                        nodes[n4 + nodenum1] = pl1[n4 + nodenum1]
                        nodes[n1 + nodenum2] = pl2[n1 + nodenum2]
                        nodes[n2 + nodenum2] = pl2[n2 + nodenum2]
                        nodes[n3 + nodenum2] = pl2[n3 + nodenum2]
                        nodes[n4 + nodenum2] = pl2[n4 + nodenum2]
                        elements[elecount] = nodes
                        elecount += 1
            return elements

        @staticmethod
        def plotbrickmember(ax, component, name, propname, subdivisions, edgelinewidth, fill, color, fontsize, facenumber,
                              alpha):
            xyz1 = component.XYZ1
            xyz2 = component.XYZ2
            xyz3 = component.XYZ3
            xyz4 = component.XYZ4
            xyz5 = component.XYZ5
            xyz6 = component.XYZ6
            xyz7 = component.XYZ7
            xyz8 = component.XYZ8
            N12 = component.N12
            N14 = component.N14
            N15 = component.N15
            xyz = [xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8]
            XX = []
            YY = []
            ZZ = []

            for coords in xyz:
                XX.append(coords[0])
                YY.append(coords[1])
                ZZ.append(coords[2])

            if name.lower() in ['y', 'yes']:
                xa = np.average(XX)
                ya = np.average(YY)
                za = np.average(ZZ)
                ax.text(za, xa, ya, component.Name, 'y', size=fontsize, horizontalalignment='center')

            if propname.lower() in ['y', 'yes']:
                prname = component.EleProps['Name']
                xa = np.average(XX)
                ya = np.average(YY)
                za = np.average(ZZ)
                ax.text(za, xa, ya, prname, 'y', size=fontsize, horizontalalignment='center')

            if facenumber in ['y', 'yes']:
                # face 1
                xa = np.average([xyz1[0], xyz2[0], xyz3[0], xyz4[0]])
                ya = np.average([xyz1[1], xyz2[1], xyz3[1], xyz4[1]])
                za = np.average([xyz1[2], xyz2[2], xyz3[2], xyz4[2]])
                ax.text(za, xa, ya, 1, 'y', size=fontsize, horizontalalignment='center')
                # face 2
                xa = np.average([xyz6[0], xyz2[0], xyz3[0], xyz7[0]])
                ya = np.average([xyz6[1], xyz2[1], xyz3[1], xyz7[1]])
                za = np.average([xyz6[2], xyz2[2], xyz3[2], xyz7[2]])
                ax.text(za, xa, ya, 2, 'y', size=fontsize, horizontalalignment='center')
                # face 3
                xa = np.average([xyz6[0], xyz5[0], xyz8[0], xyz7[0]])
                ya = np.average([xyz6[1], xyz5[1], xyz8[1], xyz7[1]])
                za = np.average([xyz6[2], xyz5[2], xyz8[2], xyz7[2]])
                ax.text(za, xa, ya, 3, 'y', size=fontsize, horizontalalignment='center')
                # face 4
                xa = np.average([xyz1[0], xyz5[0], xyz8[0], xyz4[0]])
                ya = np.average([xyz1[1], xyz5[1], xyz8[1], xyz4[1]])
                za = np.average([xyz1[2], xyz5[2], xyz8[2], xyz4[2]])
                ax.text(za, xa, ya, 4, 'y', size=fontsize, horizontalalignment='center')
                # face 5
                xa = np.average([xyz1[0], xyz5[0], xyz2[0], xyz6[0]])
                ya = np.average([xyz1[1], xyz5[1], xyz2[1], xyz6[1]])
                za = np.average([xyz1[2], xyz5[2], xyz2[2], xyz6[2]])
                ax.text(za, xa, ya, 5, 'y', size=fontsize, horizontalalignment='center')
                # face 6
                xa = np.average([xyz3[0], xyz7[0], xyz8[0], xyz4[0]])
                ya = np.average([xyz3[1], xyz7[1], xyz8[1], xyz4[1]])
                za = np.average([xyz3[2], xyz7[2], xyz8[2], xyz4[2]])
                ax.text(za, xa, ya, 6, 'y', size=fontsize, horizontalalignment='center')

                # plot faces
            if fill in ['y', 'yes']:
                # face 1
                xa = [xyz1[0], xyz2[0], xyz3[0], xyz4[0]]
                ya = [xyz1[1], xyz2[1], xyz3[1], xyz4[1]]
                za = [xyz1[2], xyz2[2], xyz3[2], xyz4[2]]
                vertices = [list(zip(za, xa, ya))]
                poly1 = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=color,
                                         edgecolor='silver')
                ax.add_collection3d(poly1)
                # face 2
                xa = [xyz6[0], xyz2[0], xyz3[0], xyz7[0]]
                ya = [xyz6[1], xyz2[1], xyz3[1], xyz7[1]]
                za = [xyz6[2], xyz2[2], xyz3[2], xyz7[2]]
                vertices = [list(zip(za, xa, ya))]
                poly1 = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=color,
                                         edgecolor='silver')
                ax.add_collection3d(poly1)
                # face 3
                xa = [xyz6[0], xyz5[0], xyz8[0], xyz7[0]]
                ya = [xyz6[1], xyz5[1], xyz8[1], xyz7[1]]
                za = [xyz6[2], xyz5[2], xyz8[2], xyz7[2]]
                vertices = [list(zip(za, xa, ya))]
                poly1 = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=color,
                                         edgecolor='silver')
                ax.add_collection3d(poly1)
                # face 4
                xa = [xyz1[0], xyz5[0], xyz8[0], xyz4[0]]
                ya = [xyz1[1], xyz5[1], xyz8[1], xyz4[1]]
                za = [xyz1[2], xyz5[2], xyz8[2], xyz4[2]]
                vertices = [list(zip(za, xa, ya))]
                poly1 = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=color,
                                         edgecolor='silver')
                ax.add_collection3d(poly1)
                # face 5
                xa = [xyz1[0], xyz5[0], xyz6[0], xyz2[0]]
                ya = [xyz1[1], xyz5[1], xyz6[1], xyz2[1]]
                za = [xyz1[2], xyz5[2], xyz6[2], xyz2[2]]
                vertices = [list(zip(za, xa, ya))]
                poly1 = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=color,
                                         edgecolor='silver')
                ax.add_collection3d(poly1)
                # face 6
                xa = [xyz3[0], xyz7[0], xyz8[0], xyz4[0]]
                ya = [xyz3[1], xyz7[1], xyz8[1], xyz4[1]]
                za = [xyz3[2], xyz7[2], xyz8[2], xyz4[2]]
                vertices = [list(zip(za, xa, ya))]
                poly1 = Poly3DCollection(vertices, alpha=alpha, linewidth=edgelinewidth, color=color,
                                         edgecolor='silver')
                ax.add_collection3d(poly1)

                # plot lines
            if subdivisions in ['y', 'yes']:
                coords, noderange, nodes = MyMath.dividecube(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, N12, N14, N15)
                nodesets = MyMath.extractbricknodesets(noderange)
                for face in nodesets.keys():
                    nodes_ = nodesets[face]['Nodes']
                    njk = len(nodes_)
                    nij = len(nodes_[0])

                    for j in range(njk):
                        n1 = nodes_[j, 0]
                        n2 = nodes_[j, nij - 1]
                        xyz1 = nodes[n1]
                        xyz2 = nodes[n2]
                        x = [xyz1[0], xyz2[0]]
                        y = [xyz1[1], xyz2[1]]
                        z = [xyz1[2], xyz2[2]]
                        ax.plot(z, x, y, lw=edgelinewidth, color='tab:gray')
                    for j in range(nij):
                        n1 = nodes_[0, j]
                        n2 = nodes_[njk - 1, j]
                        xyz1 = nodes[n1]
                        xyz2 = nodes[n2]
                        x = [xyz1[0], xyz2[0]]
                        y = [xyz1[1], xyz2[1]]
                        z = [xyz1[2], xyz2[2]]
                        ax.plot(z, x, y, lw=edgelinewidth, color='tab:gray')

            # face 1
            x = XX[0:4]
            x.append(x[0])
            y = YY[0:4]
            y.append(y[0])
            z = ZZ[0:4]
            z.append(z[0])
            ax.plot(z, x, y, lw=edgelinewidth, color='silver')

            # face 3
            x = XX[4:8]
            x.append(x[0])
            y = YY[4:8]
            y.append(y[0])
            z = ZZ[4:8]
            z.append(z[0])
            ax.plot(z, x, y, lw=edgelinewidth, color='silver')

            # face 2
            x = [XX[1], XX[5]]
            y = [YY[1], YY[5]]
            z = [ZZ[1], ZZ[5]]
            ax.plot(z, x, y, lw=edgelinewidth, color='silver')

            # face 4
            x = [XX[2], XX[6]]
            y = [YY[2], YY[6]]
            z = [ZZ[2], ZZ[6]]
            ax.plot(z, x, y, lw=edgelinewidth, color='silver')

            # face 5
            x = [XX[0], XX[4]]
            y = [YY[0], YY[4]]
            z = [ZZ[0], ZZ[4]]
            ax.plot(z, x, y, lw=edgelinewidth, color='silver')

            # face 6
            x = [XX[3], XX[7]]
            y = [YY[3], YY[7]]
            z = [ZZ[3], ZZ[7]]
            ax.plot(z, x, y, lw=edgelinewidth, color='silver')

        @staticmethod
        def plotcube(ax, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, lw, color, fill, edgecolor, alpha):
            if fill.lower() in ['n', 'no']:
                alpha = 0.0

            p1 = [xyz1[2], xyz1[0], xyz1[1]]
            p2 = [xyz2[2], xyz2[0], xyz2[1]]
            p3 = [xyz3[2], xyz3[0], xyz3[1]]
            p4 = [xyz4[2], xyz4[0], xyz4[1]]
            p5 = [xyz5[2], xyz5[0], xyz5[1]]
            p6 = [xyz6[2], xyz6[0], xyz6[1]]
            p7 = [xyz7[2], xyz7[0], xyz7[1]]
            p8 = [xyz8[2], xyz8[0], xyz8[1]]
            p=[p1, p2, p3, p4, p5, p6, p7, p8]
            if fill in ['n', 'no']:
                alpha = 0.0

            MyMath.plot_volume(ax, *p, alpha=alpha, linewidth=lw, color=color, edgecolor=edgecolor, sha=True)

        @staticmethod
        def brickvolume(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8):
            V = 0
            xa = np.average([xyz1[0], xyz2[0], xyz3[0], xyz4[0], xyz5[0], xyz6[0], xyz7[0], xyz8[0]])
            ya = np.average([xyz1[1], xyz2[1], xyz3[1], xyz4[1], xyz5[1], xyz6[1], xyz7[1], xyz8[1]])
            za = np.average([xyz1[2], xyz2[2], xyz3[2], xyz4[2], xyz5[2], xyz6[2], xyz7[2], xyz8[2]])
            ## face 1
            x1, y1, z1 = xyz1
            x2, y2, z2 = xyz2
            x3, y3, z3 = xyz4
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            x1, y1, z1 = xyz4
            x2, y2, z2 = xyz2
            x3, y3, z3 = xyz3
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            ## face 2
            x1, y1, z1 = xyz2
            x2, y2, z2 = xyz6
            x3, y3, z3 = xyz3
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            x1, y1, z1 = xyz3
            x2, y2, z2 = xyz6
            x3, y3, z3 = xyz7
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            ## face 3
            x1, y1, z1 = xyz5
            x2, y2, z2 = xyz6
            x3, y3, z3 = xyz8
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            x1, y1, z1 = xyz8
            x2, y2, z2 = xyz6
            x3, y3, z3 = xyz7
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            ## face 4
            x1, y1, z1 = xyz4
            x2, y2, z2 = xyz1
            x3, y3, z3 = xyz5
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            x1, y1, z1 = xyz4
            x2, y2, z2 = xyz5
            x3, y3, z3 = xyz8
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            ## face 5
            x1, y1, z1 = xyz1
            x2, y2, z2 = xyz2
            x3, y3, z3 = xyz5
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            x1, y1, z1 = xyz5
            x2, y2, z2 = xyz2
            x3, y3, z3 = xyz6
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            ## face 6
            x1, y1, z1 = xyz4
            x2, y2, z2 = xyz3
            x3, y3, z3 = xyz8
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)

            x1, y1, z1 = xyz8
            x2, y2, z2 = xyz3
            x3, y3, z3 = xyz7
            A = np.array([[1, x1, y1, z1], [1, x2, y2, z2], [1, x3, y3, z3], [1, xa, ya, za]])
            V1 = np.linalg.det(A) / 6
            V += abs(V1)
            return V

        @staticmethod
        def bricknodeshare(xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8):
            xc = np.average([xyz1[0], xyz2[0], xyz3[0], xyz4[0], xyz5[0], xyz6[0], xyz7[0], xyz8[0]])
            yc = np.average([xyz1[1], xyz2[1], xyz3[1], xyz4[1], xyz5[1], xyz6[1], xyz7[1], xyz8[1]])
            zc = np.average([xyz1[2], xyz2[2], xyz3[2], xyz4[2], xyz5[2], xyz6[2], xyz7[2], xyz8[2]])
            cc = [xc, yc, zc]

            x12 = np.average([xyz1[0], xyz2[0]])
            y12 = np.average([xyz1[1], xyz2[1]])
            z12 = np.average([xyz1[2], xyz2[2]])
            c12 = [x12, y12, z12]

            x14 = np.average([xyz1[0], xyz4[0]])
            y14 = np.average([xyz1[1], xyz4[1]])
            z14 = np.average([xyz1[2], xyz4[2]])
            c14 = [x14, y14, z14]

            x15 = np.average([xyz1[0], xyz5[0]])
            y15 = np.average([xyz1[1], xyz5[1]])
            z15 = np.average([xyz1[2], xyz5[2]])
            c15 = [x15, y15, z15]

            x23 = np.average([xyz2[0], xyz3[0]])
            y23 = np.average([xyz2[1], xyz3[1]])
            z23 = np.average([xyz2[2], xyz3[2]])
            c23 = [x23, y23, z23]

            x26 = np.average([xyz2[0], xyz6[0]])
            y26 = np.average([xyz2[1], xyz6[1]])
            z26 = np.average([xyz2[2], xyz6[2]])
            c26 = [x26, y26, z26]

            x34 = np.average([xyz3[0], xyz4[0]])
            y34 = np.average([xyz3[1], xyz4[1]])
            z34 = np.average([xyz3[2], xyz4[2]])
            c34 = [x34, y34, z34]

            x37 = np.average([xyz3[0], xyz7[0]])
            y37 = np.average([xyz3[1], xyz7[1]])
            z37 = np.average([xyz3[2], xyz7[2]])
            c37 = [x37, y37, z37]

            x48 = np.average([xyz4[0], xyz8[0]])
            y48 = np.average([xyz4[1], xyz8[1]])
            z48 = np.average([xyz4[2], xyz8[2]])
            c48 = [x48, y48, z48]

            x56 = np.average([xyz5[0], xyz6[0]])
            y56 = np.average([xyz5[1], xyz6[1]])
            z56 = np.average([xyz5[2], xyz6[2]])
            c56 = [x56, y56, z56]

            x58 = np.average([xyz5[0], xyz8[0]])
            y58 = np.average([xyz5[1], xyz8[1]])
            z58 = np.average([xyz5[2], xyz8[2]])
            c58 = [x58, y58, z58]

            x67 = np.average([xyz6[0], xyz7[0]])
            y67 = np.average([xyz6[1], xyz7[1]])
            z67 = np.average([xyz6[2], xyz7[2]])
            c67 = [x67, y67, z67]

            x78 = np.average([xyz7[0], xyz8[0]])
            y78 = np.average([xyz7[1], xyz8[1]])
            z78 = np.average([xyz7[2], xyz8[2]])
            c78 = [x78, y78, z78]

            x = np.average([xyz1[0], xyz2[0], xyz3[0], xyz4[0]])
            y = np.average([xyz1[1], xyz2[1], xyz3[1], xyz4[1]])
            z = np.average([xyz1[2], xyz2[2], xyz3[2], xyz4[2]])
            cf1 = [x, y, z]

            x = np.average([xyz2[0], xyz6[0], xyz7[0], xyz3[0]])
            y = np.average([xyz2[1], xyz6[1], xyz7[1], xyz3[1]])
            z = np.average([xyz2[2], xyz6[2], xyz7[2], xyz3[2]])
            cf2 = [x, y, z]

            x = np.average([xyz5[0], xyz6[0], xyz7[0], xyz8[0]])
            y = np.average([xyz5[1], xyz6[1], xyz7[1], xyz8[1]])
            z = np.average([xyz5[2], xyz6[2], xyz7[2], xyz8[2]])
            cf3 = [x, y, z]

            x = np.average([xyz5[0], xyz1[0], xyz4[0], xyz8[0]])
            y = np.average([xyz5[1], xyz1[1], xyz4[1], xyz8[1]])
            z = np.average([xyz5[2], xyz1[2], xyz4[2], xyz8[2]])
            cf4 = [x, y, z]

            x = np.average([xyz5[0], xyz1[0], xyz2[0], xyz6[0]])
            y = np.average([xyz5[1], xyz1[1], xyz2[1], xyz6[1]])
            z = np.average([xyz5[2], xyz1[2], xyz2[2], xyz6[2]])
            cf5 = [x, y, z]

            x = np.average([xyz3[0], xyz4[0], xyz7[0], xyz8[0]])
            y = np.average([xyz3[1], xyz4[1], xyz7[1], xyz8[1]])
            z = np.average([xyz3[2], xyz4[2], xyz7[2], xyz8[2]])
            cf6 = [x, y, z]

            V1 = MyMath.brickvolume(xyz1, c12, cf1, c14, c15, cf5, cc, cf4)
            V2 = MyMath.brickvolume(c12, xyz2, c23, cf1, cf5, c26, cf2, cc)
            V3 = MyMath.brickvolume(cf1, c23, xyz3, c34, cc, cf2, c37, cf6)
            V4 = MyMath.brickvolume(c14, cf1, c34, xyz4, cf4, cc, cf6, c48)
            V5 = MyMath.brickvolume(c15, cf5, cc, cf4, xyz5, c56, cf3, c58)
            V6 = MyMath.brickvolume(cf5, c26, cf2, cc, c56, xyz6, c67, cf3)
            V7 = MyMath.brickvolume(cc, cf2, c37, cf6, cf3, c67, xyz7, c78)
            V8 = MyMath.brickvolume(cf4, cc, cf6, c48, c58, cf3, c78, xyz8)

            V = V1 + V2 + V3 + V4 + V5 + V6 + V7 + V8

            return V1 / V, V2 / V, V3 / V, V4 / V, V5 / V, V6 / V, V7 / V, V8 / V

        @staticmethod
        def mirrorpoint(xyz, xyz1, xyz2, xyz3):
            for value in [xyz1, xyz2, xyz3]:
                value = list(value)
                if len(value) not in [2, 3]:
                    raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

                for i in range(len(value)):
                    if type(value[i]) is int:
                        value[i] = float(value[i])

                    if isinstance(value[i], numbers.Number) is False:
                        raise ValueError("Coordinates must be numeric values")

            x1, y1, z1 = xyz1
            x2, y2, z2 = xyz2
            x3, y3, z3 = xyz3
            x, y, z = xyz
            a, b, c = np.cross([(x2 - x1), (y2 - y1), (z2 - z1)], [(x3 - x1), (y3 - y1), (z3 - z1)])
            d = -1 * (a * x1 + b * y1 + c * z1)

            k = (-a * x - b * y - c * z - d) / (a * a + b * b + c * c)
            x2, y2, z2 = a * k + x, b * k + y, c * k + z
            symx, symy, symz = 2 * x2 - x, 2 * y2 - y, 2 * z2 - z
            return [symx, symy, symz]

        @staticmethod
        def rotatepoint(xyz, xyz1, xyz2, teta):
            for value in [xyz1, xyz2]:
                value = list(value)
                if len(value) not in [2, 3]:
                    raise ValueError("xyz must be a list contains coordinates [x, y, z] or [x, y]")

                for i in range(len(value)):
                    if type(value[i]) is int:
                        value[i] = float(value[i])

                    if isinstance(value[i], numbers.Number) is False:
                        raise ValueError("Coordinates must be numeric values")

            if isinstance(teta, numbers.Number) is False:
                raise ValueError('teta must be a numeric value')

            x1, y1, z1 = xyz1
            x2, y2, z2 = xyz2
            t = np.deg2rad(teta)
            ux, uy, uz = x2 - x1, y2 - y1, z2 - z1
            l = np.sqrt(ux ** 2 + uy ** 2 + uz ** 2)
            ux, uy, uz = ux / l, uy / l, uz / l
            cost, sint = np.cos(t), np.sin(t)
            R = np.array(
                [[cost + ux * ux * (1 - cost), ux * uy * (1 - cost) - uz * sint, ux * uz * (1 - cost) + uy * sint],
                 [uy * ux * (1 - cost) + uz * sint, cost + uy * uy * (1 - cost), uy * uz * (1 - cost) - ux * sint],
                 [uz * ux * (1 - cost) - uy * sint, uz * uy * (1 - cost) + ux * sint, cost + uz * uz * (1 - cost)]])

            xp, yp, zp = xyz
            xq, yq, zq = xp - x1, yp - y1, zp - z1
            A = list(np.matmul(R, np.array([xq, yq, zq]).transpose()).transpose())
            # print(A)
            A[0] += x1
            A[1] += y1
            A[2] += z1

            return A

        @staticmethod
        def dividetriangle(N, ele_numnodes, xyzi, xyzj, xyzk):
            Elements = {}
            Nodes = {}
            staruum = 1
            dictnodes = {}
            count = 1
            xc = (xyzi[0] + xyzj[0] + xyzk[0]) / 3
            yc = (xyzi[1] + xyzj[1] + xyzk[1]) / 3
            zc = (xyzi[2] + xyzj[2] + xyzk[2]) / 3
            centernode = [xc, yc, zc]
            Ndiv = N
            ##################  4 node elements
            if ele_numnodes == 4:
                if N <= 1 or np.remainder(Ndiv, 2) != 0:
                    raise ValueError(
                        "Triangle area with four node quadrilateral element: Number of divisions must be even positive integer value "
                        "greater than 1")

                while Ndiv >= 2:

                    XXij, YYij, ZZij, numberingij = MyMath.divideline(xyzi, xyzj, Ndiv, staruum)
                    staruum = numberingij[-1]
                    XXjk, YYjk, ZZjk, numberingjk = MyMath.divideline(xyzj, xyzk, Ndiv, staruum)
                    staruum = numberingjk[-1]
                    XXki, YYki, ZZki, numberingki = MyMath.divideline(xyzk, xyzi, Ndiv, staruum)
                    numberingki[-1] = numberingij[0]
                    staruum = numberingki[-2] + 1

                    for i in range(len(XXij)):
                        xx, yy, zz = XXij[i], YYij[i], ZZij[i]
                        nnum = int(numberingij[i])
                        Nodes[nnum] = [xx, yy, zz]

                    for i in range(len(XXij)):
                        xx, yy, zz = XXjk[i], YYjk[i], ZZjk[i]
                        nnum = int(numberingjk[i])
                        Nodes[nnum] = [xx, yy, zz]

                    for i in range(len(XXij)):
                        xx, yy, zz = XXki[i], YYki[i], ZZki[i]
                        nnum = int(numberingki[i])
                        Nodes[nnum] = [xx, yy, zz]

                    dictnodes[count] = {'ij': numberingij,
                                        'jk': numberingjk,
                                        'ki': numberingki}

                    count += 1

                    xyzij1 = [XXij[1], YYij[1], ZZij[1]]
                    xyzij2 = [XXij[-2], YYij[-2], ZZij[-2]]
                    xyzjk1 = [XXjk[1], YYjk[1], ZZjk[1]]
                    xyzjk2 = [XXjk[-2], YYjk[-2], ZZjk[-2]]
                    xyzki1 = [XXki[1], YYki[1], ZZki[1]]
                    xyzki2 = [XXki[-2], YYki[-2], ZZki[-2]]

                    xxx, yyy, zzz, numberi = MyMath.divideline(xyzij1, xyzjk2, Ndiv - 1, staruum)
                    xyzi = [xxx[1], yyy[1], zzz[1]]
                    xxx, yyy, zzz, numberi = MyMath.divideline(xyzjk1, xyzki2, Ndiv - 1, staruum)
                    xyzj = [xxx[1], yyy[1], zzz[1]]
                    xxx, yyy, zzz, numberi = MyMath.divideline(xyzki1, xyzij2, Ndiv - 1, staruum)
                    xyzk = [xxx[1], yyy[1], zzz[1]]
                    Ndiv -= 2

                count = 1
                edgeNodes = dictnodes[1]
                if N > 2:
                    for i in range(1, len(dictnodes.keys())):
                        nodes_ij_1 = dictnodes[i]['ij']
                        nodes_ij_2 = dictnodes[i + 1]['ij']
                        nodes_jk_1 = dictnodes[i]['jk']
                        nodes_jk_2 = dictnodes[i + 1]['jk']
                        nodes_ki_1 = dictnodes[i]['ki']
                        nodes_ki_2 = dictnodes[i + 1]['ki']

                        for j in range(len(nodes_ij_1) - 1):
                            nodei = nodes_ij_1[j]
                            nodej = nodes_ij_1[j + 1]
                            if j == len(nodes_ij_1) - 2:
                                nodek = nodes_jk_1[1]
                            else:
                                nodek = nodes_ij_2[j]

                            if j == 0:
                                nodel = nodes_ki_1[-2]
                            else:
                                nodel = nodes_ij_2[j - 1]
                            Elements[count] = [nodei, nodej, nodek, nodel]

                            count += 1

                        for j in range(1, len(nodes_jk_1) - 1):
                            nodei = nodes_jk_1[j]
                            nodej = nodes_jk_1[j + 1]
                            if j == len(nodes_jk_1) - 2:
                                nodek = nodes_ki_1[1]
                            else:
                                nodek = nodes_jk_2[j]

                            nodel = nodes_jk_2[j - 1]

                            Elements[count] = [nodei, nodej, nodek, nodel]
                            count += 1
                        for j in range(1, len(nodes_ki_1) - 2):
                            nodei = nodes_ki_1[j]
                            nodej = nodes_ki_1[j + 1]
                            nodek = nodes_ki_2[j]
                            nodel = nodes_ki_2[j - 1]
                            Elements[count] = [nodei, nodej, nodek, nodel]

                            count += 1

                        if i == len(dictnodes.keys()) - 1:
                            if np.remainder(N, 2) == 0:
                                cnodtag = int(nodel + 1)
                                Nodes[cnodtag] = centernode
                                nodei = nodes_ij_2[0]
                                nodej = nodes_ij_2[1]
                                nodek = cnodtag
                                nodel = nodes_ki_2[1]
                                Elements[count] = [nodei, nodej, nodek, nodel]
                                count += 1

                                nodei = nodes_ij_2[1]
                                nodej = nodes_ij_2[2]
                                nodek = nodes_jk_2[1]
                                nodel = cnodtag
                                Elements[count] = [nodei, nodej, nodek, nodel]
                                count += 1

                                nodei = nodes_jk_2[1]
                                nodej = nodes_jk_2[2]
                                nodek = nodes_ki_2[1]
                                nodel = cnodtag
                                Elements[count] = [nodei, nodej, nodek, nodel]
                                count += 1
                            else:
                                pass
                else:
                    count = 1
                    nodes_ij = edgeNodes['ij']
                    nodes_jk = edgeNodes['jk']
                    nodes_ki = edgeNodes['ki']
                    cnodtag = 7
                    Nodes[cnodtag] = centernode
                    nodei = nodes_ij[0]
                    nodej = nodes_ij[1]
                    nodek = cnodtag
                    nodel = nodes_ki[1]
                    Elements[count] = [nodei, nodej, nodek, nodel]
                    count += 1

                    nodei = nodes_ij[1]
                    nodej = nodes_ij[2]
                    nodek = nodes_jk[1]
                    nodel = cnodtag
                    Elements[count] = [nodei, nodej, nodek, nodel]
                    count += 1

                    nodei = nodes_jk[1]
                    nodej = nodes_jk[2]
                    nodek = nodes_ki[1]
                    nodel = cnodtag
                    Elements[count] = [nodei, nodej, nodek, nodel]

            ##################  9 node elements
            elif ele_numnodes == 9:
                if N <= 1 or np.remainder(Ndiv, 2) != 0:
                    raise ValueError(
                        "Triangle area with nine node quadrilateral element: Number of divisions must be even positive integer"
                        " value greater than 1")
                dictnodes2 = {}
                while Ndiv >= 2:

                    XXij, YYij, ZZij, numberingij = MyMath.divideline(xyzi, xyzj, 2 * Ndiv, staruum)
                    staruum = numberingij[-1]
                    XXjk, YYjk, ZZjk, numberingjk = MyMath.divideline(xyzj, xyzk, 2 * Ndiv, staruum)
                    staruum = numberingjk[-1]
                    XXki, YYki, ZZki, numberingki = MyMath.divideline(xyzk, xyzi, 2 * Ndiv, staruum)
                    numberingki[-1] = numberingij[0]
                    staruum = numberingki[-2] + 1

                    for i in range(len(XXij)):
                        xx, yy, zz = XXij[i], YYij[i], ZZij[i]
                        nnum = int(numberingij[i])
                        Nodes[nnum] = [xx, yy, zz]

                    for i in range(len(XXij)):
                        xx, yy, zz = XXjk[i], YYjk[i], ZZjk[i]
                        nnum = int(numberingjk[i])
                        Nodes[nnum] = [xx, yy, zz]

                    for i in range(len(XXij)):
                        xx, yy, zz = XXki[i], YYki[i], ZZki[i]
                        nnum = int(numberingki[i])
                        Nodes[nnum] = [xx, yy, zz]

                    dictnodes[count] = {'ij': numberingij,
                                        'jk': numberingjk,
                                        'ki': numberingki}

                    count += 1
                    xyzij1 = [XXij[2], YYij[2], ZZij[2]]
                    xyzij2 = [XXij[-3], YYij[-3], ZZij[-3]]
                    xyzjk1 = [XXjk[2], YYjk[2], ZZjk[2]]
                    xyzjk2 = [XXjk[-3], YYjk[-3], ZZjk[-3]]
                    xyzki1 = [XXki[2], YYki[2], ZZki[2]]
                    xyzki2 = [XXki[-3], YYki[-3], ZZki[-3]]

                    xxx, yyy, zzz, numberi = MyMath.divideline(xyzij1, xyzjk2, Ndiv - 1, staruum)
                    xyzi = [xxx[1], yyy[1], zzz[1]]
                    xxx, yyy, zzz, numberi = MyMath.divideline(xyzjk1, xyzki2, Ndiv - 1, staruum)
                    xyzj = [xxx[1], yyy[1], zzz[1]]
                    xxx, yyy, zzz, numberi = MyMath.divideline(xyzki1, xyzij2, Ndiv - 1, staruum)
                    xyzk = [xxx[1], yyy[1], zzz[1]]
                    Ndiv -= 2

                edgeNodes = dictnodes[1]
                if N > 2:
                    for i in range(len(dictnodes.keys()) - 1):
                        nodes_ij_1 = dictnodes[i + 1]['ij']
                        nodes_jk_1 = dictnodes[i + 1]['jk']
                        nodes_ki_1 = dictnodes[i + 1]['ki']
                        nodes_ij_2 = dictnodes[i + 2]['ij']
                        nodes_jk_2 = dictnodes[i + 2]['jk']
                        nodes_ki_2 = dictnodes[i + 2]['ki']
                        numberingij = []
                        numberingjk = []
                        numberingki = []
                        for j in range(2, len(nodes_ij_1) - 2, 2):
                            node1 = nodes_ij_1[j]
                            node2 = nodes_ij_2[j - 2]
                            x1, y1, z1 = Nodes[node1]
                            x2, y2, z2 = Nodes[node2]
                            x3, y3, z3 = (x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2
                            Nodes[staruum] = [x3, y3, z3]
                            numberingij.append(staruum)
                            staruum += 1

                        for j in range(2, len(nodes_jk_1) - 2, 2):
                            node1 = nodes_jk_1[j]
                            node2 = nodes_jk_2[j - 2]
                            x1, y1, z1 = Nodes[node1]
                            x2, y2, z2 = Nodes[node2]
                            x3, y3, z3 = (x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2
                            Nodes[staruum] = [x3, y3, z3]
                            numberingjk.append(staruum)
                            staruum += 1

                        for j in range(2, len(nodes_ki_1) - 2, 2):
                            node1 = nodes_ki_1[j]
                            node2 = nodes_ki_2[j - 2]
                            x1, y1, z1 = Nodes[node1]
                            x2, y2, z2 = Nodes[node2]
                            x3, y3, z3 = (x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2
                            Nodes[staruum] = [x3, y3, z3]
                            numberingki.append(staruum)
                            staruum += 1

                        dictnodes2[i + 1] = {'ij': numberingij,
                                             'jk': numberingjk,
                                             'ki': numberingki}

                    count = 1
                    for i in range(1, len(dictnodes.keys())):
                        nodes_ij_1 = dictnodes[i]['ij']
                        nodes_ij_2 = dictnodes[i + 1]['ij']
                        nodes_jk_1 = dictnodes[i]['jk']
                        nodes_jk_2 = dictnodes[i + 1]['jk']
                        nodes_ki_1 = dictnodes[i]['ki']
                        nodes_ki_2 = dictnodes[i + 1]['ki']

                        nodes_ij_m = dictnodes2[i]['ij']
                        nodes_jk_m = dictnodes2[i]['jk']
                        nodes_ki_m = dictnodes2[i]['ki']

                        for j in range(0, len(nodes_ij_1) - 1, 2):
                            node1 = nodes_ij_1[j]
                            node2 = nodes_ij_1[j + 2]
                            if j == len(nodes_ij_1) - 3:
                                node3 = nodes_jk_1[2]
                            else:
                                node3 = nodes_ij_2[j]

                            if j == 0:
                                node4 = nodes_ki_1[-3]
                            else:
                                node4 = nodes_ij_2[j - 2]

                            node5 = nodes_ij_1[j + 1]

                            if j == len(nodes_ij_1) - 3:
                                node6 = nodes_jk_1[1]
                            else:
                                # print(j / 2)
                                node6 = nodes_ij_m[int(j / 2)]

                            if j == 0:
                                node7 = nodes_ki_m[-1]
                            elif j == len(nodes_ij_1) - 3:
                                node7 = nodes_jk_m[0]
                            else:
                                node7 = nodes_ij_2[j - 1]

                            if j == 0:
                                node8 = nodes_ki_1[-2]
                            else:
                                node8 = nodes_ij_m[int(j / 2 - 1)]

                            node9 = staruum
                            x5, y5, z5 = Nodes[node5]
                            x7, y7, z7 = Nodes[node7]
                            x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                            Nodes[node9] = [x9, y9, z9]
                            Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                            count += 1
                            staruum += 1

                        for j in range(2, len(nodes_jk_1) - 1, 2):
                            node1 = nodes_jk_2[j - 2]
                            node2 = nodes_jk_1[j]
                            node3 = nodes_jk_1[j + 2]
                            if j == len(nodes_jk_1) - 3:
                                node4 = nodes_ki_1[2]
                            else:
                                node4 = nodes_jk_2[j]

                            node5 = nodes_jk_m[int(j / 2 - 1)]
                            node6 = nodes_jk_1[j + 1]

                            if j == len(nodes_ij_1) - 3:
                                node7 = nodes_ki_1[1]
                            else:
                                node7 = nodes_jk_m[int(j / 2)]

                            if j == len(nodes_ij_1) - 3:
                                node8 = nodes_ki_m[0]
                            else:
                                node8 = nodes_jk_2[j - 1]

                            node9 = staruum
                            x5, y5, z5 = Nodes[node5]
                            x7, y7, z7 = Nodes[node7]
                            x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                            Nodes[node9] = [x9, y9, z9]
                            Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                            count += 1
                            staruum += 1

                        for j in range(2, len(nodes_ki_1) - 3, 2):
                            node1 = nodes_ki_1[j + 2]
                            node2 = nodes_ki_2[j]
                            node3 = nodes_ki_2[j - 2]
                            node4 = nodes_ki_1[j]
                            node5 = nodes_ki_m[int(j / 2)]
                            node6 = nodes_ki_2[j - 1]
                            node7 = nodes_ki_m[int(j / 2 - 1)]
                            node8 = nodes_ki_1[j + 1]

                            node9 = staruum
                            x5, y5, z5 = Nodes[node5]
                            x7, y7, z7 = Nodes[node7]
                            x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                            Nodes[node9] = [x9, y9, z9]
                            Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                            count += 1
                            staruum += 1

                        if i == len(dictnodes.keys()) - 1:
                            if np.remainder(N, 2) == 0:
                                cnodtag = staruum
                                staruum += 1
                                Nodes[cnodtag] = centernode

                                node1 = nodes_ij_2[0]
                                node2 = nodes_ij_2[2]
                                node3 = cnodtag
                                node4 = nodes_ki_2[2]
                                node5 = nodes_ij_2[1]

                                x2, y2, z2 = Nodes[node2]
                                x3, y3, z3 = Nodes[node3]
                                x4, y4, z4 = Nodes[node4]
                                x5, y5, z5 = Nodes[node5]

                                x6, y6, z6 = (x2 + x3) / 2, (y2 + y3) / 2, (z2 + z3) / 2
                                x7, y7, z7 = (x3 + x4) / 2, (y3 + y4) / 2, (z3 + z4) / 2
                                node6 = staruum
                                no1 = node6
                                staruum += 1
                                node7 = staruum
                                no2 = node7
                                staruum += 1
                                Nodes[node6] = [x6, y6, z6]
                                Nodes[node7] = [x7, y7, z7]

                                node8 = nodes_ki_2[3]

                                node9 = staruum
                                staruum += 1
                                x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                                Nodes[node9] = [x9, y9, z9]
                                Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                                count += 1

                                node1 = nodes_ij_2[2]
                                node2 = nodes_ij_2[4]
                                node3 = nodes_jk_2[2]
                                node4 = cnodtag

                                node5 = nodes_ij_2[3]
                                node6 = nodes_jk_2[1]

                                x3, y3, z3 = Nodes[node3]
                                x4, y4, z4 = Nodes[node4]
                                x5, y5, z5 = Nodes[node5]

                                x7, y7, z7 = (x3 + x4) / 2, (y3 + y4) / 2, (z3 + z4) / 2
                                node7 = staruum
                                no3 = node7
                                staruum += 1
                                Nodes[node7] = [x7, y7, z7]

                                node8 = no1
                                node9 = staruum
                                staruum += 1
                                x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                                Nodes[node9] = [x9, y9, z9]

                                Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                                count += 1

                                node1 = nodes_jk_2[2]
                                node2 = nodes_jk_2[4]
                                node3 = nodes_ki_2[2]
                                node4 = cnodtag
                                node5 = nodes_jk_2[3]
                                node6 = nodes_ki_2[1]
                                node7 = no2
                                node8 = no3

                                x5, y5, z5 = Nodes[node5]
                                x7, y7, z7 = Nodes[node7]
                                node9 = staruum
                                staruum += 1
                                x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                                Nodes[node9] = [x9, y9, z9]
                                Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                                count += 1
                            else:
                                pass
                else:
                    count = 1
                    nodes_ij = edgeNodes['ij']
                    nodes_jk = edgeNodes['jk']
                    nodes_ki = edgeNodes['ki']
                    staruum = 13
                    cnodtag = staruum
                    staruum += 1
                    Nodes[cnodtag] = centernode

                    node1 = nodes_ij[0]
                    node2 = nodes_ij[2]
                    node3 = cnodtag
                    node4 = nodes_ki[2]
                    node5 = nodes_ij[1]

                    x2, y2, z2 = Nodes[node2]
                    x3, y3, z3 = Nodes[node3]
                    x4, y4, z4 = Nodes[node4]
                    x5, y5, z5 = Nodes[node5]

                    x6, y6, z6 = (x2 + x3) / 2, (y2 + y3) / 2, (z2 + z3) / 2
                    x7, y7, z7 = (x3 + x4) / 2, (y3 + y4) / 2, (z3 + z4) / 2
                    node6 = staruum
                    no1 = node6
                    staruum += 1
                    node7 = staruum
                    no2 = node7
                    staruum += 1
                    Nodes[node6] = [x6, y6, z6]
                    Nodes[node7] = [x7, y7, z7]

                    node8 = nodes_ki[3]

                    node9 = staruum
                    staruum += 1
                    x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                    Nodes[node9] = [x9, y9, z9]
                    Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                    count += 1

                    node1 = nodes_ij[2]
                    node2 = nodes_ij[4]
                    node3 = nodes_jk[2]
                    node4 = cnodtag

                    node5 = nodes_ij[3]
                    node6 = nodes_jk[1]

                    x3, y3, z3 = Nodes[node3]
                    x4, y4, z4 = Nodes[node4]
                    x5, y5, z5 = Nodes[node5]

                    x7, y7, z7 = (x3 + x4) / 2, (y3 + y4) / 2, (z3 + z4) / 2
                    node7 = staruum
                    no3 = node7
                    staruum += 1
                    Nodes[node7] = [x7, y7, z7]

                    node8 = no1
                    node9 = staruum
                    staruum += 1
                    x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                    Nodes[node9] = [x9, y9, z9]

                    Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
                    count += 1

                    node1 = nodes_jk[2]
                    node2 = nodes_jk[4]
                    node3 = nodes_ki[2]
                    node4 = cnodtag
                    node5 = nodes_jk[3]
                    node6 = nodes_ki[1]
                    node7 = no2
                    node8 = no3

                    x5, y5, z5 = Nodes[node5]
                    x7, y7, z7 = Nodes[node7]
                    node9 = staruum
                    staruum += 1
                    x9, y9, z9 = (x5 + x7) / 2, (y5 + y7) / 2, (z5 + z7) / 2
                    Nodes[node9] = [x9, y9, z9]
                    Elements[count] = [node1, node2, node3, node4, node5, node6, node7, node8, node9]

            ##################  3 node elements
            elif ele_numnodes == 3:
                if N < 1:
                    raise ValueError(
                        "Triangle area with three node triangular element: Number of divisions must be positive integer value")

                XXij, YYij, ZZij, numberingij = MyMath.divideline(xyzi, xyzj, Ndiv, staruum)
                staruum = numberingij[-1]
                XXjk, YYjk, ZZjk, numberingjk = MyMath.divideline(xyzj, xyzk, Ndiv, staruum)
                staruum = numberingjk[-1]
                XXki, YYki, ZZki, numberingki = MyMath.divideline(xyzk, xyzi, Ndiv, staruum)
                numberingki[-1] = numberingij[0]
                staruum = numberingki[-2]

                for i in range(len(XXij)):
                    xx, yy, zz = XXij[i], YYij[i], ZZij[i]
                    nnum = int(numberingij[i])
                    Nodes[nnum] = [xx, yy, zz]

                for i in range(len(XXij)):
                    xx, yy, zz = XXjk[i], YYjk[i], ZZjk[i]
                    nnum = int(numberingjk[i])
                    Nodes[nnum] = [xx, yy, zz]

                for i in range(len(XXij)):
                    xx, yy, zz = XXki[i], YYki[i], ZZki[i]
                    nnum = int(numberingki[i])
                    Nodes[nnum] = [xx, yy, zz]

                dictnodes = {'ij': numberingij,
                             'jk': numberingjk,
                             'ki': numberingki}

                dictnodes2 = {}
                dictnodes2[0] = numberingij
                numberingik = list(numberingki)
                numberingik.reverse()

                for i in range(1, Ndiv - 1):
                    nodei = numberingik[i]
                    nodej = numberingjk[i]

                    xyzi = Nodes[nodei]
                    xyzj = Nodes[nodej]

                    XXij, YYij, ZZij, numbering = MyMath.divideline(xyzi, xyzj, Ndiv - i, staruum)

                    numbering[0] = nodei
                    numbering[-1] = nodej
                    staruum = numbering[-2]

                    dictnodes2[i] = numbering

                    for i in range(len(XXij)):
                        xx, yy, zz = XXij[i], YYij[i], ZZij[i]
                        nnum = int(numbering[i])
                        Nodes[nnum] = [xx, yy, zz]

                dictnodes2[Ndiv - 1] = [numberingki[1], numberingjk[-2]]
                dictnodes2[Ndiv] = [numberingjk[-1]]
                edgeNodes = dictnodes
                count = 1

                for i in range(len(dictnodes2) - 1):
                    nodes_ij_1 = dictnodes2[i]
                    nodes_ij_2 = dictnodes2[i + 1]
                    for j in range(len(nodes_ij_2)):
                        nodei = nodes_ij_1[j]
                        nodej = nodes_ij_1[j + 1]
                        nodek = nodes_ij_2[j]
                        Elements[count] = [nodei, nodej, nodek]
                        count += 1
                        if j != len(nodes_ij_2) - 1:
                            nodei = nodes_ij_1[j + 1]
                            nodej = nodes_ij_2[j + 1]
                            nodek = nodes_ij_2[j]
                            Elements[count] = [nodei, nodej, nodek]
                            count += 1

            return Nodes, Elements, edgeNodes

        def plot_area(ax, *p, alpha=0.7, linewidth=1.0, color='b', edgecolor='silver',sha=True):
            if len(p) == 4:
                p1, p2, p3, p4 = p
                x = np.array([[p1[0], p2[0]],[p4[0], p3[0]]])
                y = np.array([[p1[1], p2[1]],[p4[1], p3[1]]])
                z = np.array([[p1[2], p2[2]],[p4[2], p3[2]]])
            elif len(p) == 3:
                p1, p2, p3 = p
                p4 = p3

            else:
                return
            x = np.array([[p1[0], p2[0]], [p4[0], p3[0]]])
            y = np.array([[p1[1], p2[1]], [p4[1], p3[1]]])
            z = np.array([[p1[2], p2[2]], [p4[2], p3[2]]])
            if alpha == 0:
                ax.plot_wireframe(x, y, z, rstride=1, cstride=1,linewidth=linewidth,color=edgecolor, antialiased=False,
                            edgecolors=edgecolor)
            else:
                ax.plot_surface(x, y, z, rstride=1, cstride=1,linewidth=linewidth,color=color,alpha=alpha, antialiased=False,
                                edgecolors=edgecolor, shade=sha)

        def plot_volume(ax, *p, alpha=0.7, linewidth=1.0, color='b', edgecolor='silver',sha=True):
            if len(p) == 8:
                p1, p2, p3, p4, p5, p6, p7, p8 = p
            else:
                return

            x = np.array([[p1[0], p2[0]],[p5[0], p6[0]],[p8[0], p7[0]],[p4[0], p3[0]],[p1[0], p2[0]]])
            y = np.array([[p1[1], p2[1]],[p5[1], p6[1]],[p8[1], p7[1]],[p4[1], p3[1]],[p1[1], p2[1]]])
            z = np.array([[p1[2], p2[2]],[p5[2], p6[2]],[p8[2], p7[2]],[p4[2], p3[2]],[p1[2], p2[2]]])
            if alpha == 0:
                ax.plot_wireframe(x, y, z, rstride=1, cstride=1,linewidth=linewidth,color=edgecolor, antialiased=False,
                            edgecolors=edgecolor)
            else:
                ax.plot_surface(x, y, z, rstride=1, cstride=1,linewidth=linewidth,color=color,alpha=alpha, antialiased=False,
                                edgecolors=edgecolor, shade=sha)

            MyMath.plot_area(ax, p1, p5, p8, p4, alpha=alpha, linewidth=linewidth, color=color, edgecolor=edgecolor, sha=sha)
            MyMath.plot_area(ax, p2, p6, p7, p3, alpha=alpha, linewidth=linewidth, color=color, edgecolor=edgecolor, sha=sha)

        @staticmethod
        def Transform_g2l(V, Vx, Vy, Vz):
            ex_g = [1, 0, 0]
            ey_g = [0, 1, 0]
            ez_g = [0, 0, 1]

            ex_l = Vx / np.linalg.norm(Vx)
            ey_l = Vy / np.linalg.norm(Vy)
            ez_l = Vz / np.linalg.norm(Vz)

            Tr = np.array([
                [np.dot(ex_g, ex_l), np.dot(ey_g, ex_l), np.dot(ez_g, ex_l)],
                [np.dot(ex_g, ey_l), np.dot(ey_g, ey_l), np.dot(ez_g, ey_l)],
                [np.dot(ex_g, ez_l), np.dot(ey_g, ez_l), np.dot(ez_g, ez_l)]
            ])
            V_L = np.matmul(Tr, V)
            return V_L

        @staticmethod
        def Transform_l2g(V, Vx, Vy, Vz):
            ex_g = [1, 0, 0]
            ey_g = [0, 1, 0]
            ez_g = [0, 0, 1]

            ex_l = Vx / np.linalg.norm(Vx)
            ey_l = Vy / np.linalg.norm(Vy)
            ez_l = Vz / np.linalg.norm(Vz)

            Tr = np.array([
                [np.dot(ex_g, ex_l), np.dot(ex_g, ey_l), np.dot(ex_g, ez_l)],
                [np.dot(ey_g, ex_l), np.dot(ey_g, ey_l), np.dot(ey_g, ez_l)],
                [np.dot(ez_g, ex_l), np.dot(ez_g, ey_l), np.dot(ez_g, ez_l)]
            ])
            V_G = np.matmul(Tr, V)
            return V_G

        @staticmethod
        def data_contourplot_quad(n, max_data, min_data, p1, p2, p3, p4, data):
            c = np.array(data) + abs(min_data)
            max_data += abs(min_data)

            XX1, YY1, ZZ1, numbering = MyMath.divideline(p1, p2, n, 1)
            XX2, YY2, ZZ2, numbering = MyMath.divideline(p4, p3, n, 1)

            c = np.array(c) / max_data
            c_1 = np.linspace(c[0], c[1], n + 1)
            c_2 = np.linspace(c[3], c[2], n + 1)

            X = []
            Y = []
            Z = []
            C = []
            for i in range(len(XX1)):
                xyz1 = [XX1[i], YY1[i], ZZ1[i]]
                xyz2 = [XX2[i], YY2[i], ZZ2[i]]
                XX, YY, ZZ, numbering = MyMath.divideline(xyz1, xyz2, n, 1)
                X.append(XX)
                Y.append(YY)
                Z.append(ZZ)
                C.append(np.linspace(c_1[i], c_2[i], n + 1))

            X = np.array(X)
            Y = np.array(Y)
            Z = np.array(Z)
            return X, Y, Z, C

        @staticmethod
        def data_contourplot_tri(n, max_data, min_data, p1, p2, p3, data):

            xm, ym, zm = np.mean([p1[0], p2[0], p3[0]]), np.mean([p1[1], p2[1], p3[1]]), np.mean([p1[2], p2[2], p3[2]])
            pm = [xm, ym, zm]
            p12 = (np.array(p1) + np.array(p2)) / 2
            p23 = (np.array(p2) + np.array(p3)) / 2
            p13 = (np.array(p1) + np.array(p3)) / 2

            data_m = np.mean(np.array(data))
            data1, data2, data3 = data
            data12 = (data[0] + data[1]) / 2
            data23 = (data[2] + data[1]) / 2
            data13 = (data[0] + data[2]) / 2

            data_1 = [data_m, data13, data1, data12]
            data_2 = [data_m, data12, data2, data23]
            data_3 = [data_m, data23, data3, data13]
            X = []
            Y = []
            Z = []
            C = []
            Xx, Yy, Zz, Cc = MyMath.data_contourplot_quad(int(n / 2), max_data, min_data, pm, p13, p1, p12, data_1)
            X.append(Xx)
            Y.append(Yy)
            Z.append(Zz)
            C.append(Cc)
            Xx, Yy, Zz, Cc = MyMath.data_contourplot_quad(int(n / 2), max_data, min_data, pm, p12, p2, p23, data_2)
            X.append(Xx)
            Y.append(Yy)
            Z.append(Zz)
            C.append(Cc)
            Xx, Yy, Zz, Cc = MyMath.data_contourplot_quad(int(n / 2), max_data, min_data, pm, p23, p3, p13, data_3)
            X.append(Xx)
            Y.append(Yy)
            Z.append(Zz)
            C.append(Cc)

            X = np.array(X)
            Y = np.array(Y)
            Z = np.array(Z)
            return X, Y, Z, C

        @staticmethod
        def data_contourplot_line(n, max_data, min_data, p1, p2, data):
            c_ = np.array(data) + abs(min_data)
            max_data += abs(min_data)

            X, Y, Z, numbering = MyMath.divideline(p1, p2, n, 1)

            c_ = np.array(c_) / max_data
            C = np.linspace(c_[0], c_[1], n + 1)
            X = np.array(X)
            Y = np.array(Y)
            Z = np.array(Z)
            return X, Y, Z, C

class MyFEM:
    @staticmethod
    def N_T3(r, s):
        N1 = 1 - r - s
        N2 = r
        N3 = s
        return np.array([N1, N2, N3])

    @staticmethod
    def jac_T3(X, Y):
        x1, x2, x3 = X
        y1, y2, y3 = Y
        xr = -1 * x1 + x2
        xs = -1 * x1 + x3
        yr = -1 * y1 + y2
        ys = -1 * y1 + y3
        J = np.array([[xr, yr], [xs, ys]])
        return J, np.linalg.det(J)

    @staticmethod
    def nodalforce_T3(fb, coord, xyzi, xyzj, xyzk):
        xyzi = np.array(xyzi)
        xyzj = np.array(xyzj)
        xyzk = np.array(xyzk)
        xyzm = (xyzi + xyzj + xyzk) / 3
        Vx, Vy, Vz = MyMath.localcoord_tri(xyzi, xyzj, xyzk)

        fb_l = fb
        if coord.lower() in ['g', 'global']:
            fb_l = np.array(MyMath.Transform_g2l(fb, Vx, Vy, Vz))

        Pi = MyMath.Transform_g2l(xyzi - xyzm, Vx, Vy, Vz)[:2]
        Pj = MyMath.Transform_g2l(xyzj - xyzm, Vx, Vy, Vz)[:2]
        Pk = MyMath.Transform_g2l(xyzk - xyzm, Vx, Vy, Vz)[:2]

        fb12 = np.array(fb_l[:2]).reshape(2, 1)
        X = np.array([Pi[0], Pj[0], Pk[0]])
        Y = np.array([Pi[1], Pj[1], Pk[1]])
        rsw = [[0.16666666667, 0.16666666667, 1 / 3], [0.6666666666667, 0.16666666667, 1 / 3],
               [0.16666666667, 0.6666666666667, 1 / 3]]
        R12 = np.zeros((6, 1))
        R3 = np.zeros((3, 1))
        J, det_J = MyFEM.jac_T3(X, Y)

        for rsw_ in rsw:
            rr, ss, ww = rsw_
            N = MyFEM.N_T3(rr, ss)
            N26 = np.array([[N[0], 0, N[1], 0, N[2], 0], [0, N[0], 0, N[1], 0, N[2]]])
            N13 = N.reshape(3, 1)
            R12 += 0.5 * np.matmul(np.transpose(N26), fb12) * det_J * ww
            R3 += 0.5 * N13 * det_J * fb_l[2] * ww

        R_l = np.zeros((3, 3))
        for i in range(3):
            R_l[i][0] = R12[i * 2]
            R_l[i][1] = R12[i * 2 + 1]
            R_l[i][2] = R3[i]
        R_g = np.array([MyMath.Transform_l2g(x, Vx, Vy, Vz) for x in R_l])
        return R_l, R_g

    @staticmethod
    def nodalstress_T3(*S):
        Sg = np.array(S)
        N = np.zeros([3, 3])

        # node 1
        r, s = -1.732050808, -1.732050808
        # N = MyFEM.N_Q4(r, s)
        N[0, :] = MyFEM.N_Q4(r, s)

        # node 2
        r, s = 1.732050808, -1.732050808
        N[1, :] = MyFEM.N_Q4(r, s)

        # node 3
        r, s = 1.732050808, 1.732050808
        N[2, :] = MyFEM.N_Q4(r, s)

        # node 4
        r, s = -1.732050808, 1.732050808
        N[3, :] = MyFEM.N_Q4(r, s)

        S_ = np.matmul(N, np.transpose(Sg)).reshape((1, 4))
        return S_[0]

    @staticmethod
    def N_Q4(r, s):
        N1 = 0.25 * (1 - r) * (1 - s)
        N2 = 0.25 * (1 + r) * (1 - s)
        N3 = 0.25 * (1 + r) * (1 + s)
        N4 = 0.25 * (1 - r) * (1 + s)
        return np.array([N1, N2, N3, N4])

    @staticmethod
    def jac_Q4(r, s, X, Y):
        x1, x2, x3, x4 = X
        y1, y2, y3, y4 = Y
        xr = 0.25 * ((s - 1) * x1 + (1 - s) * x2 + (1 + s) * x3 - (1 + s) * x4)
        xs = 0.25 * ((r - 1) * x1 - (1 + r) * x2 + (1 + r) * x3 + (1 - r) * x4)
        yr = 0.25 * ((s - 1) * y1 + (1 - s) * y2 + (1 + s) * y3 - (1 + s) * y4)
        ys = 0.25 * ((r - 1) * y1 - (1 + r) * y2 + (1 + r) * y3 + (1 - r) * y4)
        J = np.array([[xr, yr], [xs, ys]])
        return J, np.linalg.det(J)

    @staticmethod
    def nodalforce_Q4(fb, coord, xyzi, xyzj, xyzk, xyzl):
        xyzi = np.array(xyzi)
        xyzj = np.array(xyzj)
        xyzk = np.array(xyzk)
        xyzl = np.array(xyzl)
        xyzm = (xyzi + xyzj + xyzk + xyzl) / 4
        Vx, Vy, Vz = MyMath.localcoord_quad(xyzi, xyzj, xyzk, xyzl)
        fb_l = fb
        if coord.lower() in ['g', 'global']:
            fb_l = np.array(MyMath.Transform_g2l(fb, Vx, Vy, Vz))

        Pi = MyMath.Transform_g2l(xyzi - xyzm, Vx, Vy, Vz)[:2]
        Pj = MyMath.Transform_g2l(xyzj - xyzm, Vx, Vy, Vz)[:2]
        Pk = MyMath.Transform_g2l(xyzk - xyzm, Vx, Vy, Vz)[:2]
        Pl = MyMath.Transform_g2l(xyzl - xyzm, Vx, Vy, Vz)[:2]

        fb12 = np.array(fb_l[:2]).reshape(2, 1)
        X = np.array([Pi[0], Pj[0], Pk[0], Pl[0]])
        Y = np.array([Pi[1], Pj[1], Pk[1], Pl[1]])
        r = [0.57735, -0.57735]
        s = [0.57735, -0.57735]
        R12 = np.zeros((8, 1))
        R3 = np.zeros((4, 1))
        for rr in r:
            for ss in s:
                N = MyFEM.N_Q4(rr, ss)
                N28 = np.array([[N[0], 0, N[1], 0, N[2], 0, N[3], 0], [0, N[0], 0, N[1], 0, N[2], 0, N[3]]])
                N14 = N.reshape(4, 1)
                J, det_J = MyFEM.jac_Q4(rr, ss, X, Y)
                R12 += np.matmul(np.transpose(N28), fb12) * det_J
                R3 += N14 * det_J * fb_l[2]

        R_l = np.zeros((4, 3))
        for i in range(4):
            R_l[i][0] = R12[i * 2]
            R_l[i][1] = R12[i * 2 + 1]
            R_l[i][2] = R3[i]
        R_g = np.array([MyMath.Transform_l2g(x, Vx, Vy, Vz) for x in R_l])
        return R_l, R_g

    @staticmethod
    def nodalstress_Q4(*S):
        Sg = np.array(S)
        N = np.zeros([4, 4])

        # node 1
        r, s = -1.732050808, -1.732050808
        # N = MyFEM.N_Q4(r, s)
        N[0,:] = MyFEM.N_Q4(r, s)

        # node 2
        r, s = 1.732050808, -1.732050808
        N[1,:] = MyFEM.N_Q4(r, s)

        # node 3
        r, s = 1.732050808, 1.732050808
        N[2,:] = MyFEM.N_Q4(r, s)

        # node 4
        r, s = -1.732050808, 1.732050808
        N[3,:] = MyFEM.N_Q4(r, s)

        S_ = np.matmul(N, np.transpose(Sg)).reshape((1,4))
        return S_[0]

    @staticmethod
    def N_Q9(r, s):
        L1r = -0.5 * r * (1 - r)
        L2r = (1 + r) * (1 - r)
        L3r = 0.5 * r * (1 + r)
        L1s = -0.5 * s * (1 - s)
        L2s = (1 + s) * (1 - s)
        L3s = 0.5 * s * (1 + s)
        N1 = L1r * L1s
        N2 = L3r * L1s
        N3 = L3r * L3s
        N4 = L1r * L3s
        N5 = L2r * L1s
        N6 = L3r * L2s
        N7 = L2r * L3s
        N8 = L1r * L2s
        N9 = L2r * L2s
        return np.array([N1, N2, N3, N4, N5, N6, N7, N8, N9])

    @staticmethod
    def jac_Q9(r, s, X, Y):
        X = np.array(X)
        Y = np.array(Y)
        L1r = -0.5 * r * (1 - r)
        L2r = (1 + r) * (1 - r)
        L3r = 0.5 * r * (1 + r)
        L1s = -0.5 * s * (1 - s)
        L2s = (1 + s) * (1 - s)
        L3s = 0.5 * s * (1 + s)
        N1r = L1s * (r - 0.5)
        N1s = L1r * (s - 0.5)
        N2r = L1s * (r + 0.5)
        N2s = L3r * (s - 0.5)
        N3r = L3s * (r + 0.5)
        N3s = L3r * (s + 0.5)
        N4r = L3s * (r - 0.5)
        N4s = L1r * (s + 0.5)
        N5r = L1s * (-2 * r)
        N5s = L2r * (s - 0.5)
        N6r = L2s * (r + 0.5)
        N6s = L3r * (-2 * s)
        N7r = L3s * (-2 * r)
        N7s = L2r * (s + 0.5)
        N8r = L2s * (r - 0.5)
        N8s = L1r * (-2 * s)
        N9r = L2s * (-2 * r)
        N9s = L2r * (-2 * s)
        Nr = np.array([N1r, N2r, N3r, N4r, N5r, N6r, N7r, N8r, N9r])
        Ns = np.array([N1s, N2s, N3s, N4s, N5s, N6s, N7s, N8s, N9s])

        xr = np.matmul(Nr, X)
        xs = np.matmul(Ns, X)
        yr = np.matmul(Nr, Y)
        ys = np.matmul(Ns, Y)
        J = np.array([[xr, yr], [xs, ys]])
        return J, np.linalg.det(J)

    @staticmethod
    def nodalforce_Q9(fb, coord, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8, xyz9):
        xyz1 = np.array(xyz1)
        xyz2 = np.array(xyz2)
        xyz3 = np.array(xyz3)
        xyz4 = np.array(xyz4)
        xyzm = (xyz1 + xyz2 + xyz3 + xyz4) / 4
        Vx, Vy, Vz = MyMath.localcoord_quad(xyz1, xyz2, xyz3, xyz4)
        fb_l = fb
        if coord.lower() in ['g', 'global']:
            fb_l = np.array(MyMath.Transform_g2l(fb, Vx, Vy, Vz))

        P1 = MyMath.Transform_g2l(xyz1 - xyzm, Vx, Vy, Vz)[:2]
        P2 = MyMath.Transform_g2l(xyz2 - xyzm, Vx, Vy, Vz)[:2]
        P3 = MyMath.Transform_g2l(xyz3 - xyzm, Vx, Vy, Vz)[:2]
        P4 = MyMath.Transform_g2l(xyz4 - xyzm, Vx, Vy, Vz)[:2]
        P5 = MyMath.Transform_g2l(xyz5 - xyzm, Vx, Vy, Vz)[:2]
        P6 = MyMath.Transform_g2l(xyz6 - xyzm, Vx, Vy, Vz)[:2]
        P7 = MyMath.Transform_g2l(xyz7 - xyzm, Vx, Vy, Vz)[:2]
        P8 = MyMath.Transform_g2l(xyz8 - xyzm, Vx, Vy, Vz)[:2]
        P9 = MyMath.Transform_g2l(xyz9 - xyzm, Vx, Vy, Vz)[:2]

        fb12 = np.array(fb_l[:2]).reshape(2, 1)
        X = np.array([P1[0], P2[0], P3[0], P4[0], P5[0], P6[0], P7[0], P8[0], P9[0]])
        Y = np.array([P1[1], P2[1], P3[1], P4[1], P5[1], P6[1], P7[1], P8[1], P9[1]])

        ai = 5 / 9
        aj = 8 / 9
        rsw = [[-0.7745966, -0.7745966, ai * ai], [0.7745966, -0.7745966, ai * ai],
               [0.7745966, 0.7745966, ai * ai], [-0.7745966, 0.7745966, ai * ai],
               [0.0, -0.7745966, ai * aj], [0.7745966, 0.0, ai * aj],
               [0.0, 0.7745966, ai * aj], [-0.7745966, 0.0, ai * aj],
               [0.0, 0.0, aj * aj]]
        R12 = np.zeros((18, 1))
        R3 = np.zeros((9, 1))
        for rsw_ in rsw:
            rr, ss, ww = rsw_
            N = MyFEM.N_Q9(rr, ss)

            N218 = np.array([
                [N[0], 0, N[1], 0, N[2], 0, N[3], 0, N[4], 0, N[5], 0, N[6], 0, N[7], 0, N[8], 0],
                [0, N[0], 0, N[1], 0, N[2], 0, N[3], 0, N[4], 0, N[5], 0, N[6], 0, N[7], 0, N[8]]
            ])
            N19 = N.reshape(9, 1)
            J, det_J = MyFEM.jac_Q9(rr, ss, X, Y)
            R12 += np.matmul(np.transpose(N218), fb12) * det_J * ww
            R3 += N19 * det_J * fb_l[2] * ww


        R_l = np.zeros((9, 3))
        for i in range(9):
            R_l[i][0] = R12[i * 2]
            R_l[i][1] = R12[i * 2 + 1]
            R_l[i][2] = R3[i]
        R_g = np.array([MyMath.Transform_l2g(x, Vx, Vy, Vz) for x in R_l])

        return R_l, R_g

    @staticmethod
    def N_B8(r, s, t):

        N6 = (1 - r) * (1 - s) * (1 - t) / 8
        N5 = (1 - r) * (1 - s) * (1 + t) / 8
        N1 = (1 + r) * (1 - s) * (1 + t) / 8
        N2 = (1 + r) * (1 - s) * (1 - t) / 8
        N7 = (1 - r) * (1 + s) * (1 - t) / 8
        N8 = (1 - r) * (1 + s) * (1 + t) / 8
        N4 = (1 + r) * (1 + s) * (1 + t) / 8
        N3 = (1 + r) * (1 + s) * (1 - t) / 8

        return np.array([N1, N2, N3, N4, N5, N6, N7, N8])

    @staticmethod
    def jac_B8(r, s, t, X, Y, Z):
        X = np.array(X)
        Y = np.array(Y)
        Z = np.array(Z)

        N1r = 1 * (1 - s) * (1 + t) / 8
        N1s = -1 * (1 + r) * (1 + t) / 8
        N1t = 1 * (1 + r) * (1 - s) / 8

        N2r = 1 * (1 - s) * (1 - t) / 8
        N2s = -1 * (1 + r) * (1 - t) / 8
        N2t = -1 * (1 + r) * (1 - s) / 8

        N3r = 1 * (1 + s) * (1 - t) / 8
        N3s = 1 * (1 + r) * (1 - t) / 8
        N3t = -1 * (1 + r) * (1 + s) / 8

        N4r = 1 * (1 + s) * (1 + t) / 8
        N4s = 1 * (1 + r) * (1 + t) / 8
        N4t = 1 * (1 + r) * (1 + s) / 8

        N5r = -1 * (1 - s) * (1 + t) / 8
        N5s = -1 * (1 - r) * (1 + t) / 8
        N5t = 1 * (1 - r) * (1 - s) / 8

        N6r = -1 * (1 - s) * (1 - t) / 8
        N6s = -1 * (1 - r) * (1 - t) / 8
        N6t = -1 * (1 - r) * (1 - s) / 8

        N7r = -1 * (1 + s) * (1 - t) / 8
        N7s = 1 * (1 - r) * (1 - t) / 8
        N7t = -1 * (1 - r) * (1 + s) / 8

        N8r = -1 * (1 + s) * (1 + t) / 8
        N8s = 1 * (1 - r) * (1 + t) / 8
        N8t = 1 * (1 - r) * (1 + s) / 8

        Nr = np.array([N1r, N2r, N3r, N4r, N5r, N6r, N7r, N8r])
        Ns = np.array([N1s, N2s, N3s, N4s, N5s, N6s, N7s, N8s])
        Nt = np.array([N1t, N2t, N3t, N4t, N5t, N6t, N7t, N8t])

        xr = np.matmul(Nr, X)
        xs = np.matmul(Ns, X)
        xt = np.matmul(Nt, X)
        yr = np.matmul(Nr, Y)
        yt = np.matmul(Nt, Y)
        ys = np.matmul(Ns, Y)
        zr = np.matmul(Nr, Z)
        zt = np.matmul(Nt, Z)
        zs = np.matmul(Ns, Z)
        J = np.array([[xr, yr, zr], [xs, ys, zs], [xt, yt, zt]])

        return J, np.linalg.det(J)

    @staticmethod
    def nodalforce_B8(fb, xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8):
        X = []
        Y = []
        Z = []
        for xyz_ in [xyz1, xyz2, xyz3, xyz4, xyz5, xyz6, xyz7, xyz8]:
            X.append(xyz_[0])
            Y.append(xyz_[1])
            Z.append(xyz_[2])

        X = np.array(X)
        Y = np.array(Y)
        Z = np.array(Z)

        fb_l = np.array(fb).reshape(3, 1)

        r = [0.57735, -0.57735]
        s = [0.57735, -0.57735]
        t = [0.57735, -0.57735]
        R = np.zeros((24, 1))
        for rr in r:
            for ss in s:
                for tt in t:
                    N = MyFEM.N_B8(rr, ss, tt)
                    N24 = np.array([
                        [N[0], 0, 0, N[1], 0, 0, N[2], 0, 0, N[3], 0, 0, N[4], 0, 0, N[5], 0, 0, N[6], 0, 0, N[7], 0,
                         0],
                        [0, N[0], 0, 0, N[1], 0, 0, N[2], 0, 0, N[3], 0, 0, N[4], 0, 0, N[5], 0, 0, N[6], 0, 0, N[7],
                         0],
                        [0, 0, N[0], 0, 0, N[1], 0, 0, N[2], 0, 0, N[3], 0, 0, N[4], 0, 0, N[5], 0, 0, N[6], 0, 0, N[7]]
                    ])
                    J, det_J = MyFEM.jac_B8(rr, ss, tt, X, Y, Z)
                    R += np.matmul(np.transpose(N24), fb_l) * det_J

        return R.reshape((8,3))

