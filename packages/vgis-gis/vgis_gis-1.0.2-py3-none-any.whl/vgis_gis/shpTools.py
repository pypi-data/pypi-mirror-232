"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: shpTools.py
@Date: Create in 2021/1/22 13:43
@Description: 对shpfile文件的操作类
@ Software: PyCharm
# shp处理：gadl,shpfile,shapely、Fiona等类

===================================
"""

import csv
import os
from shutil import copyfile

import geopandas as gpd
import pandas as pd
from osgeo import gdal
from osgeo import ogr, osr
from rtree import index
from shapely.geometry import box
from shapely.ops import cascaded_union

from vgis_utils.commonTools import CommonHelper


class ShpFileOperator:
    # 初始化
    def __init__(self, shp_file_path):
        self.shp_file_path = shp_file_path
        # 为了支持中文路径，请添加下面这句代码
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        # 为了使属性表字段支持中文，请添加下面这句
        gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
        # 注册所有的驱动
        ogr.RegisterAll()
        ds = ogr.Open(shp_file_path, 0)
        if ds == None:
            print("打开文件【%s】失败！", shp_file_path)
            return
        print("打开文件【%s】成功！", shp_file_path)
        self.shp_dataset = ds

    # 将整个shp转换为geojson
    def convert_all_feature_to_geojson(self, geojson_file_path):
        shp_lyr = self.shp_dataset.GetLayer(0)
        # 创建结果Geojson
        geojson_name = os.path.basename(geojson_file_path)
        out_driver = ogr.GetDriverByName('GeoJSON')
        out_ds = out_driver.CreateDataSource(geojson_file_path)
        if out_ds.GetLayer(geojson_name):
            out_ds.DeleteLayer(geojson_name)
        out_lyr = out_ds.CreateLayer(geojson_name, shp_lyr.GetSpatialRef())
        out_lyr.CreateFields(shp_lyr.schema)
        out_feat = ogr.Feature(out_lyr.GetLayerDefn())
        # 生成结果文件
        for feature in shp_lyr:
            out_feat.SetGeometry(feature.geometry())
            for j in range(feature.GetFieldCount()):
                out_feat.SetField(j, feature.GetField(j))
            out_lyr.CreateFeature(out_feat)
        feature.Destroy()
        self.shp_dataset.Destroy()
        del out_ds

    # 将shp中每个要素转换为geojson，用shp里指定字段值来命名geojson
    def convert_each_feature_to_geojson(self, geojson_dir_path, geojson_name_field_name):
        shp_lyr = self.shp_dataset.GetLayer(0)
        feature_count = shp_lyr.GetFeatureCount()
        for t in range(feature_count):
            feature = shp_lyr.GetNextFeature()
            geom = feature.GetGeometryRef()
            # 创建结果Geojson
            # 获取前六位编码
            geojson_name = feature.GetFieldAsString(geojson_name_field_name)[0:6]
            geojson_file_path = geojson_dir_path + CommonHelper.get_dash_in_system() + geojson_name + ".geoJson"
            if os.path.exists(geojson_file_path):
                os.remove(geojson_file_path)
            out_driver = ogr.GetDriverByName('GeoJSON')
            out_ds = out_driver.CreateDataSource(geojson_file_path)
            if out_ds.GetLayer(geojson_name):
                out_ds.DeleteLayer(geojson_name)
            out_lyr = out_ds.CreateLayer(geojson_name, shp_lyr.GetSpatialRef())
            out_lyr.CreateFields(shp_lyr.schema)
            out_feat = ogr.Feature(out_lyr.GetLayerDefn())
            # 生成结果文件
            out_feat.SetGeometry(feature.geometry())
            for j in range(feature.GetFieldCount()):
                out_feat.SetField(j, feature.GetField(j))
            out_lyr.CreateFeature(out_feat)
            del out_ds
        feature.Destroy()
        self.shp_dataset.Destroy()

    # 读取shp数据，获取所有字段值信息
    def get_shp_all_feild(self):
        all_data_list = []
        # 为了支持中文路径，请添加下面这句代码
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        # 为了使属性表字段支持中文，请添加下面这句
        gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
        # 注册所有的驱动
        ogr.RegisterAll()
        ds = ogr.Open(self.shp_file_path, 0)
        layer = ds.GetLayer(0)
        feature_count = layer.GetFeatureCount()
        lydefn = layer.GetLayerDefn()
        fieldlist = []
        for i in range(lydefn.GetFieldCount()):
            fddefn = lydefn.GetFieldDefn(i)
            fddict = {'name': fddefn.GetName(), 'type': fddefn.GetType(),
                      'width': fddefn.GetWidth(), 'decimal': fddefn.GetPrecision()}
            fieldlist += [fddict]
        for t in range(feature_count):
            # for t in range(6):
            feature = layer.GetNextFeature()
            geom = feature.GetGeometryRef()
            polygonextent = geom.GetEnvelope()
            obj = {}
            obj["序号"] = t + 1
            obj["空间范围"] = polygonextent
            # 获取所有字段
            for fd in fieldlist:
                field_name = fd['name']
                field_type = fd['type']
                # FID开头的字段不需要
                if field_name.startswith("FID") is False:
                    if field_type == 2:
                        # 对于浮点数字保留小数点后三位
                        value = format(feature.GetField(fd['name']), '.5f')
                        obj[field_name] = str(value)
                    else:
                        obj[field_name] = feature.GetFieldAsString(fd['name'])
            all_data_list.append(obj)
        # close
        ds.Destroy()
        return all_data_list

    # 获取shp的坐标系信息
    def get_coordsInfo_of_shp(self, shpFilePath):
        print(shpFilePath)
        # 为了支持中文路径，请添加下面这句代码
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        # 为了使属性表字段支持中文，请添加下面这句
        gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
        # 注册所有的驱动
        ogr.RegisterAll()
        ds = ogr.Open(shpFilePath, 0)
        layer = ds.GetLayer(0)
        # 得到坐标系信息
        spatialref = layer.GetSpatialRef()
        src_wkt = spatialref.ExportToWkt()
        coordNameArray = src_wkt.split("\"")
        coordName = coordNameArray[1]
        print("shp的坐标系名称：" + coordName)
        # close
        ds.Destroy()

    # 通过csv生成shp数据
    # csv第一行为字段类型（int,float,vgis_string,geometry）
    # 第二行为字段名(最后一列为空间字段名：几何对象)
    # 第三行起为数据（最后一列为坐标串，格式为wtk）
    # POINT(6 10)
    # LINESTRING(3 4,10 50,20 25)
    # POLYGON((1 1,5 1,5 5,1 5,1 1),(2 2,2 3,3 3,3 2,2 2))
    def convert_csv_data_into_shp(self, csv_path, shp_path, shp_name, geometry_type):
        feature_count = 0
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        gdal.SetConfigOption("SHAPE_ENCODING", "")
        source = osr.SpatialReference()
        source.ImportFromEPSG(4326)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        data_source = driver.CreateDataSource(shp_path)
        if geometry_type == "point":
            layer = data_source.CreateLayer(shp_name, source, ogr.wkbPolygon)
        if geometry_type == "line":
            layer = data_source.CreateLayer(shp_name, source, ogr.wkbLineString)
        if geometry_type == "polygon":
            layer = data_source.CreateLayer(shp_name, source, ogr.wkbPolygon)

        line_num = 0
        field_type_list = []
        field_name_list = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                line_num = line_num + 1
                if line_num == 1:
                    for i in range(len(line)):
                        if i < len(line) - 1:
                            field_type_list.append(line[i])
                if line_num == 2:
                    for i in range(len(line)):
                        if i < len(line) - 1:
                            # 字段类型 http://www.manongjc.com/article/61807.html
                            if field_type_list[i] == "int":
                                field_name = ogr.FieldDefn(line[i], ogr.OFTInteger)
                                field_name.SetWidth(2550)
                                layer.CreateField(field_name)
                            if field_type_list[i] == "float":
                                field_name = ogr.FieldDefn(line[i], ogr.OFTReal)
                                field_name.SetWidth(8)
                                field_name.SetPrecision(6)
                                layer.CreateField(field_name)
                            if field_type_list[i] == "vgis_string":
                                field_name = ogr.FieldDefn(line[i], ogr.OFTString)
                                field_name.SetWidth(2550)
                                layer.CreateField(field_name)
                            field_name_list.append(line[i])
                if line_num > 2:
                    feature_count = feature_count + 1
                    feature = ogr.Feature(layer.GetLayerDefn())
                    for i in range(len(line)):
                        if i < len(line) - 1:
                            feature.SetField(field_name_list[i], line[i])
                        else:
                            # point1x point1y,point2x point2y,...pointnx,pointny
                            coords = line[i]
                            # WKT 和geometry https: // blog.csdn.net / mwp5212 / article / details / 77448008
                            if geometry_type == "point":
                                wkt = "POINT(%f)" % (coords)
                            if geometry_type == "line":
                                wkt = "LINESTRING(%f)" % (coords)
                            if geometry_type == "polygon":
                                wkt = "POLYGON((%f))" % (coords)
                            geometry = ogr.CreateGeometryFromWkt(wkt)
                            feature.SetGeometry(geometry)
                            layer.CreateFeature(feature)
        data_source.Destroy()
        return feature_count

    # 复制shapefile
    def copy_shape(self, origin_shp_path):
        (file_pre_path, temp_filename) = os.path.split(origin_shp_path)
        fname, ext = os.path.splitext(origin_shp_path)
        base_name = os.path.basename(fname)
        origin_file_path_list = []
        dest_file_path_list = []
        origin_file_path_list.append(os.path.join(file_pre_path, base_name + ".shp"))
        dest_file_path_list.append(os.path.join(file_pre_path, base_name + "_copy.shp"))
        origin_file_path_list.append(os.path.join(file_pre_path, base_name + ".shx"))
        dest_file_path_list.append(os.path.join(file_pre_path, base_name + "_copy.shx"))
        origin_file_path_list.append(os.path.join(file_pre_path, base_name + ".prj"))
        dest_file_path_list.append(os.path.join(file_pre_path, base_name + "_copy.prj"))
        origin_file_path_list.append(os.path.join(file_pre_path, base_name + ".dbf"))
        dest_file_path_list.append(os.path.join(file_pre_path, base_name + "_copy.dbf"))
        for i in range(len(origin_file_path_list)):
            copyfile(origin_file_path_list[i], dest_file_path_list[i])

    # 将shp进行上下翻转
    def updown_reverse_shp(self, input_shp_path):
        # 注册所有驱动
        gdal.AllRegister()
        # 解决中文路径乱码问题
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        gdal.SetConfigOption("SHAPE_ENCODING", "")
        driver = ogr.GetDriverByName('ESRI Shapefile')
        origin_pFeatureDataset = driver.Open(input_shp_path, 1)
        origin_pFeaturelayer = origin_pFeatureDataset.GetLayer(0)
        origin_featureLayerNum = origin_pFeaturelayer.GetFeatureCount(0)
        layer_minY = origin_pFeaturelayer.GetExtent()[2]
        layer_maxY = origin_pFeaturelayer.GetExtent()[3]
        # 获取要素
        for t in range(0, origin_featureLayerNum):
            origin_ofeature = origin_pFeaturelayer.GetFeature(t)
            origin_geom = origin_ofeature.GetGeometryRef()
            reverse_geom = self.handle_reverse_geomety(origin_geom, layer_minY, layer_maxY)
            origin_ofeature.SetGeometry(reverse_geom)
            origin_pFeaturelayer.SetFeature(origin_ofeature)
        origin_pFeaturelayer = None
        origin_pFeatureDataset = None

    def _handle_reverse_geomety(self, origin_geom, minY, maxY):
        # minY = origin_geom.GetEnvelope()[2]
        # maxY = origin_geom.GetEnvelope()[3]
        offsetY = abs(maxY - minY)
        origin_geom_wkt = origin_geom.ExportToWkt()
        point_list = origin_geom_wkt.lstrip("'POLYGON ((").rstrip("))'").split(",")
        point1_x = float(point_list[0].split(" ")[0])
        point1_y = minY + (offsetY - (float(point_list[0].split(" ")[1]) - minY))
        point2_x = float(point_list[1].split(" ")[0])
        point2_y = minY + (offsetY - (float(point_list[1].split(" ")[1]) - minY))
        point3_x = float(point_list[2].split(" ")[0])
        point3_y = minY + (offsetY - (float(point_list[2].split(" ")[1]) - minY))
        point4_x = float(point_list[3].split(" ")[0])
        point4_y = minY + (offsetY - (float(point_list[3].split(" ")[1]) - minY))
        reverse_geom_wkt = "POLYGON((%f %f,%f %f,%f %f,%f %f,%f %f))" % (
            point1_x, point1_y, point2_x, point2_y, point3_x, point3_y, point4_x, point4_y, point1_x, point1_y)
        return ogr.CreateGeometryFromWkt(reverse_geom_wkt)

    @staticmethod
    def convert_jgw_to_gdaltransform(jgwFilePath: str) -> list:
        """
        将世界投影文件jpw格式转为gdal的投影六参数数组
        jpw格式为：0.0000197051\n 0.0000000000\n 0.0000000000\n -0.0000197051\n 104.595572656171356\n 38.815550616869423\n
            #  A 表示影像数据与矢量数据在 X 方向的比例关系;X方向 每像素的精度值
            #  D 表示影像数据与矢量数据在 Y方向的比例关系, 但它为负值, 这是由于空间坐标系与影像数据的存储坐标系在 Y方向上相反, 要匹配, 必须将 E 设为负值;Y方向 每像素的精度值
            #  E、F 表示影像数据的左上角点的像元对应的空间坐标的 X、Y 坐标;
            #  B、C 表示影像数据的旋转参数, 但是在 MapObjects2. 0 中不支持影像数据的旋转, 因此 这两个参数的数值是被忽略的, 缺省记录为 0。
        gdal transform格式为[114.0, 0.000001, 0, 34.0, 0, -0.000001]
            # 左上角点坐标X
            # x方向的分辨
            # 旋转系数，如果为0，就是标准的正北向图像
            # 左上角点坐标Y
            # 旋转系数，如果为0，就是标准的正北向图像
            # Y方向的分辨率

        :param jgwFilePath: 世界投影文件路径
        :return: gdal的几何投影六参数数组
        """
        f = open(jgwFilePath)
        line = f.readline()
        row = 0
        while line:
            row += 1
            if row == 1:
                x_scale_value = line.rstrip("\n")
            if row == 2:
                x_rotate_value = line.rstrip("\n")
            if row == 3:
                y_rotate_value = line.rstrip("\n")
            if row == 4:
                y_scale_value = line.rstrip("\n")
            if row == 5:
                x_leftupper_value = line.rstrip("\n")
            if row == 6:
                y_leftupper_value = line.rstrip("\n")
            line = f.readline()
        f.close()
        gdal_transform = [float(x_leftupper_value), float(x_scale_value), float(x_rotate_value),
                          float(y_leftupper_value),
                          float(y_rotate_value),
                          float(y_scale_value)]
        return gdal_transform

    @staticmethod
    # 栅格转矢量
    def raster_to_vector(src_file, src_transform, dst_file, output_format):
        # 在使用 GDAL 栅格转矢量时，一般默认输入的栅格数据带有地理信息，如果输入的图片不带有地理信息，则会出现矢量化结果与原图上下反转；
        if gdal.GetDriverCount() == 0:
            gdal.AllRegister()

        if ogr.GetDriverCount() == 0:
            ogr.RegisterAll()

        # 获取地理坐标时应注意的问题
        # os.environ["GDAL_DATA"] = "E:/gdal232/data"  # 设置环境变量，防止在设置、获取投影坐标时出错
        os.environ["GDAL_FILENAME_IS_UTF8"] = "NO"  # 解决中文乱码问题
        # # 为了支持中文路径，请添加下面这句代码
        # gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        # # 为了使属性表字段支持中文，请添加下面这句
        # gdal.SetConfigOption("SHAPE_ENCODING", "CP936")

        # 读取栅格数据
        src_ds = gdal.Open(src_file, gdal.GA_ReadOnly)

        if src_ds is None:
            print("输入图像数据为空！")
            return 0

        # 自定义坐标系
        # 如果输入的栅格数据没有地理信息的话，需要自定义坐标系，否则矢量化结果与原数据程垂直镜像对称
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromEPSG(4326)  # WGS84地理坐标系

        src_ds.SetProjection(spatial_reference.ExportToWkt())

        # 坐标信
        # 左上角点坐标X
        # x方向的分辨
        # 旋转系数，如果为0，就是标准的正北向图像
        # 左上角点坐标Y
        # 旋转系数，如果为0，就是标准的正北向图像
        # Y方向的分辨率

        # padf_transform = [114.0, 0.000001, 0, 34.0, 0, -0.000001]

        src_ds.SetGeoTransform(src_transform)

        # 根据输出格式创建输出矢量文件
        driver = ogr.GetDriverByName(output_format)

        if driver is None:
            print(f"{output_format} driver not available.")
            return 0

        # 根据文件名创建输出矢量数据集
        dst_ds = driver.CreateDataSource(dst_file)

        if dst_ds is None:
            print("创建矢量文件失败！")
            return 0

        # spatial_reference = src_ds.GetSpatialRef()

        # 定义空间参考，与输入图像相同
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromWkt(src_ds.GetProjectionRef())

        # 创建图层
        layer = dst_ds.CreateLayer("DstLayer", spatial_ref, ogr.wkbPolygon)

        if layer is None:
            src_ds = None
            dst_ds = None
            return 0

        # 创建属性表，只有一个字段即“value”，里面保存对应栅格的像元值
        field_defn = ogr.FieldDefn("value", ogr.OFTInteger)

        if layer.CreateField(field_defn) != ogr.OGRERR_NONE:
            print("Creating Name field failed.")
            return 0

        # 获取图像的第一个波段
        src_band = src_ds.GetRasterBand(1)

        # 调用栅格矢量化
        gdal.Polygonize(src_band, None, layer, 0, [], callback=None)

        dst_ds.SyncToDisk()

        # src_ds.FlushCache()

        src_ds = None  # 关闭文件
        dst_ds = None

        del src_ds
        del dst_ds
        gdal.GDALDestroyDriverManager()

        return 1

    @staticmethod
    # 对多边形进行接边
    def join_edge_polygon(input_shp_path: str, output_shp_path: str, buffer_distance: float) -> None:
        """
        对多边形shp进行接边，针对同一地物被分割的情况

        :param input_shp_path: 输入的多边形shp文件路径
        :param output_shp_path: 接边后的多边形shp文件路径
        :param buffer_distance: 接边时对外缓冲半价，与矢量数据单位一致，0.1度-->10公里,0.001度为100米,0.00001度为1米
        """
        # 进行多边形的自动接边
        shp_df = gpd.read_file(input_shp_path)
        buffered_data = shp_df.buffer(buffer_distance)
        # 这个方法是将所有的多边形合并成了一个多边形，不对
        adjacent_polygons = buffered_data.unary_union
        # driver = ogr.GetDriverByName('ESRI Shapefile')
        # # 打开输入数据源
        # output_ds = ogr.Open(input_shp_path)
        # # 获取输入图层
        # output_layer = output_ds.GetLayer(0)
        # # 进行多边形的自动接边
        # output_layer = output_layer.UnionCascaded()
        # # 保存合并后的多边形为shp文件
        # driver.CopyDataSource(output_ds, output_shp_path)

        # 创建R树索引
        idx = index.Index()
        for i, polygon in shp_df.iterrows():
            idx.insert(i, polygon.geometry.bounds)

        # 创建一个空的列表用于存储相邻的多边形
        adjacent_polygons = []

        # 遍历所有多边形
        for i, polygon in shp_df.iterrows():
            is_adjacent = False

            # 使用R树索引进行相邻关系查询
            potential_neighbors = list(idx.intersection(polygon.geometry.bounds))

            # 检查当前多边形与潜在邻居的相邻关系
            for neighbor_idx in potential_neighbors:
                neighbor_polygon = shp_df.loc[neighbor_idx].geometry
                if polygon.geometry.touches(neighbor_polygon):
                    # 如果相邻，则将当前多边形与邻居合并
                    merged_polygon = cascaded_union([polygon.geometry, neighbor_polygon])
                    polygon.geometry = merged_polygon
                    is_adjacent = True
                    break

            # 如果当前多边形与邻居不相邻，则将其添加到相邻多边形列表中
            if not is_adjacent:
                adjacent_polygons.append(polygon.geometry)

        # 创建新的GeoDataFrame，包含合并后的多边形
        new_data = gpd.GeoDataFrame(geometry=adjacent_polygons)

        new_data.to_file(output_shp_path, driver='ESRI Shapefile')

    @staticmethod
    # 获取符合条件的shp要素，生成新shp
    def get_shp_by_where(self, inShp, outputShp, field, fieldValue):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(inShp, 1)
        layer = dataSource.GetLayer()

        # 新建DataSource，Layer
        out_ds = driver.CreateDataSource(outputShp)
        out_lyr = out_ds.CreateLayer(outputShp, layer.GetSpatialRef(), ogr.wkbPolygon)
        def_feature = out_lyr.GetLayerDefn()

        for feature in layer:
            geom = feature.GetGeometryRef()
            value = feature.GetField(field)
            if value == fieldValue:
                out_feature = ogr.Feature(def_feature)
                out_feature.SetGeometry(geom)
                out_lyr.CreateFeature(out_feature)
            out_feature = None

        out_ds.FlushCache()
        del dataSource, out_ds

    @staticmethod
    def remain_overlap_low_feature_of_two_shp(first_shp: str, second_shp: str, low_overlap_ratio: float,
                                              out_shp: str) -> None:
        """
        计算两个shp中不相交，或相交小于指定重叠率的要素，保留第一个shp中满足条件的要素，并生成新的shp

        @param first_shp: 第一个shp文件路径
        @param second_shp: 第二个shp文件路径
        @param low_overlap_ratio: 指定重叠率
        @param out_shp:新的shp文件路径
        """

        # 加载第一个 shapefile
        first_shapefile = gpd.read_file(first_shp)

        # 加载第二个 shapefile
        second_shapefile = gpd.read_file(second_shp)

        # 找到相交的要素
        intersected_features = gpd.overlay(first_shapefile, second_shapefile, how='intersection')

        # 计算第一个 shapefile 中每个要素的面积
        first_shapefile['area'] = first_shapefile.geometry.area

        # 计算重叠率
        overlap_ratio = intersected_features.geometry.area / first_shapefile.area

        # 保留重叠率小于指定最小重叠率 的要素
        low_overlap_features = first_shapefile[overlap_ratio < low_overlap_ratio]

        # # 计算第一个 shapefile 中不与第二个相交的要素，这个方式用第二个去裁切第一个，保留的是裁切后的要素，不是我们想要的
        # non_intersected_features = gpd.overlay(first_shapefile,second_shapefile, how='difference')

        # 我们需要的是，计算两个shp不相交的要素，并保留第一个shp里不相交的要素
        # 创建 R 树索引
        idx = index.Index()
        for i, second_feature in second_shapefile.iterrows():
            idx.insert(i, second_feature.geometry.bounds)

        non_intersected_features = []

        # 遍历第一个 shapefile 的要素
        for i, first_feature in first_shapefile.iterrows():
            # 获取第一个要素的边界框
            bounds = first_feature.geometry.bounds

            # 使用 R 树索引查找相交的要素
            intersected_indices = list(idx.intersection(bounds))

            # 判断是否有相交的要素
            if len(intersected_indices) == 0:
                non_intersected_features.append(first_feature)
        non_intersected_gpd = gpd.GeoDataFrame(non_intersected_features, columns=first_shapefile.columns)
        non_intersected_gpd.set_geometry('geometry')

        # 最后的结果是 第一个shp里没有相交+第一个shp里相交率很低（低于指定重叠率），并对结果去重
        union_result = low_overlap_features.append(non_intersected_features)

        # 根据空间形状进行去重
        dissolved_gdf = union_result.drop_duplicates(subset=["geometry"], keep='first')

        result_shp_dir = os.path.join(os.getcwd(), "shp", "remove_non_building")
        if not os.path.exists(result_shp_dir):
            os.makedirs(result_shp_dir)

        # 保存结果到新的 shapefile
        dissolved_gdf.to_file(out_shp)

    @staticmethod
    def remain_overlap_low_feature_of_two_shp2(first_shp: str, second_shp: str, low_overlap_ratio: float,
                                               out_shp: str) -> None:
        """
        计算两个shp中不相交，或相交小于指定重叠率的要素，保留第一个shp中满足条件的要素，并生成新的shp

        @param first_shp: 第一个shp文件路径
        @param second_shp: 第二个shp文件路径
        @param low_overlap_ratio: 指定重叠率
        @param out_shp:新的shp文件路径
        """

        from osgeo import ogr

        # 打开第一个shp文件
        shp1 = ogr.Open(first_shp)
        layer1 = shp1.GetLayer()

        # 打开第二个shp文件
        shp2 = ogr.Open(second_shp)
        layer2 = shp2.GetLayer()

        # 创建新的shp文件
        driver = ogr.GetDriverByName('ESRI Shapefile')
        output_path = out_shp
        output_shp = driver.CreateDataSource(output_path)
        output_layer = output_shp.CreateLayer('result', geom_type=ogr.wkbPolygon)

        # 复制第一个shp文件的属性字段
        layerDefn = layer1.GetLayerDefn()
        for i in range(layerDefn.GetFieldCount()):
            fieldDefn = layerDefn.GetFieldDefn(i)
            output_layer.CreateField(fieldDefn)

        # 遍历第一个shp文件的要素
        for feature1 in layer1:
            geometry1 = feature1.GetGeometryRef()
            intersection_found = False

            # 遍历第二个shp文件的要素
            for feature2 in layer2:
                geometry2 = feature2.GetGeometryRef()
                intersection = geometry1.Intersection(geometry2)
                if not intersection.IsEmpty():
                    # 计算相交面积率
                    intersection_area = intersection.GetArea()
                    geometry1_area = geometry1.GetArea()
                    intersection_ratio = intersection_area / geometry1_area

                    if intersection_ratio >= low_overlap_ratio:
                        intersection_found = True
                        break

            # 如果没有相交或相交面积率小于阈值，则保留第一个shp文件的要素
            if not intersection_found:
                output_feature = ogr.Feature(layerDefn)
                output_feature.SetGeometry(geometry1)
                for i in range(layerDefn.GetFieldCount()):
                    output_feature.SetField(i, feature1.GetField(i))
                output_layer.CreateFeature(output_feature)
                output_feature = None

        # 关闭数据源
        shp1 = None
        shp2 = None
        output_shp = None

    @staticmethod
    # 与arcgis算的一样
    def overlap_segment_result_of_building2(segment_shp_path: str, building_shp_path: str, overlap_threshold: float,
                                            result_shp_path: str):
        from osgeo import ogr

        # 打开第一个 SHP 文件
        shp1 = ogr.Open(segment_shp_path)
        layer1 = shp1.GetLayer()

        # 打开第二个 SHP 文件
        shp2 = ogr.Open(building_shp_path)
        layer2 = shp2.GetLayer()

        # 创建输出 SHP 文件
        driver = ogr.GetDriverByName('ESRI Shapefile')
        output_shp = driver.CreateDataSource(result_shp_path)
        output_layer = output_shp.CreateLayer('result', geom_type=ogr.wkbPolygon)

        # 从第一个 SHP 文件中复制属性字段到输出 SHP 文件
        feature_defn = layer1.GetLayerDefn()
        for i in range(feature_defn.GetFieldCount()):
            output_layer.CreateField(feature_defn.GetFieldDefn(i))

        # 遍历第一个 SHP 文件的要素
        for feature1 in layer1:
            geom1 = feature1.GetGeometryRef()

            # 遍历第二个 SHP 文件的要素
            for feature2 in layer2:
                geom2 = feature2.GetGeometryRef()

                # 判断两个要素是否相交
                if geom1.Intersects(geom2):
                    # 保留第一个 SHP 文件的要素
                    output_feature = ogr.Feature(feature_defn)
                    output_feature.SetGeometry(geom1)

                    # 复制属性值到输出 SHP 文件
                    for i in range(feature_defn.GetFieldCount()):
                        output_feature.SetField(i, feature1.GetField(i))

                    # 将要素添加到输出图层
                    output_layer.CreateFeature(output_feature)

                    # 释放资源
                    output_feature = None
                    break

            # 重置第二个 SHP 文件的要素指针
            layer2.ResetReading()

        # 关闭数据源
        shp1 = None
        shp2 = None
        output_shp = None

    @staticmethod
    # 算的不准
    def overlap_segment_result_of_building(segment_shp_path: str, building_shp_path: str, overlap_threshold: float,
                                           result_shp_path: str) -> str:
        """
        对分割结果shp与建筑物shp进行overlap计算，得到有交集的分割结果新shp

        :param segment_shp_path: 分割结果shp文件路径
        :param building_shp_path: 建筑物shp文件路径
        :param overlap_threshold: 重叠面积百分比的阈值
        :param logger: 日志对象
        :return: 交集后的分割结果shp文件
        """

        # 该算法没有考虑multipolygon相交问题？

        # 分割结果shp文件
        segment_shp_gdf = gpd.read_file(segment_shp_path)

        # 使用 explode() 将 MultiPolygon 拆分为单独的 Polygon
        # segment_shp_gdf_exploded = segment_shp_gdf.explode()

        # 建筑物shp文件
        building_shp_gdf = gpd.read_file(building_shp_path)

        # 创建一个空的 GeoDataFrame 用于存储转换后的 Polygon
        # gdf_polygon = gpd.GeoDataFrame(columns=segment_shp_gdf.columns)

        # # 遍历原始 GeoDataFrame 中的每一行
        # for idx, row in segment_shp_gdf.iterrows():
        #     # 检查几何对象类型是否为 MultiPolygon
        #     if row.geometry.type == 'MultiPolygon':
        #         # 将 MultiPolygon 拆分为单独的 Polygon
        #         polygons = row.geometry
        #         for polygon in polygons:
        #             # 创建新的行，并将单独的 Polygon 添加到新的 GeoDataFrame
        #             new_row = row
        #             new_row.geometry = polygon
        #             gdf_polygon = gdf_polygon.append(new_row, ignore_index=True)
        #     else:
        #         # 对于非 MultiPolygon 类型的几何对象，直接添加到新的 GeoDataFrame
        #         gdf_polygon = gdf_polygon.append(row, ignore_index=True)
        #
        # # 打印转换后的结果
        # print(gdf_polygon.head())

        # 建立建筑物的R树空间索引，建筑物要素很多，建索引是为了提高效率
        idx = index.Index()
        for i, geom in enumerate(building_shp_gdf.geometry):
            idx.insert(i, geom.bounds)

        # 存储满足重叠要求的要素
        selected_features = []

        # 遍历分割结果shp文件的要素
        for segment_feature in segment_shp_gdf.iterrows():
            segment_geom = segment_feature[1].geometry

            segment_geom_bounds = segment_geom.bounds

            # 使用R树索引进行快速空间查询
            intersecting_indices = list(idx.intersection(segment_geom_bounds))

            # 判断分割结果shp文件的要素是否与建筑物shp文件的要素有重叠
            for i in intersecting_indices:
                builing_shp_geom = building_shp_gdf.geometry[i]

                # 判断重叠面积百分比是否满足阈值
                intersection_area = segment_geom.intersection(builing_shp_geom).area
                overlap_percentage = intersection_area / segment_geom.area
                # overlap_percentage2 = intersection_area / builing_shp_geom.area
                if overlap_percentage >= overlap_threshold:
                    # if overlap_percentage >= overlap_threshold or overlap_percentage2 >= overlap_threshold:
                    selected_features.append(segment_feature[1])
                    break

            # # 遍历建筑物个shp文件的要素,效率慢
            # for building_feature in building_shp_gdf.iterrows():
            #     builing_geom = building_feature[1].geometry
            #     # 判断是否存在相交关系
            #     if builing_geom.intersects(segment_geom):
            #         # 判断重叠面积百分比是否满足阈值
            #         intersection_area = segment_geom.intersection(builing_geom).area
            #         overlap_percentage = intersection_area / segment_geom.area
            #         # overlap_percentage2 = intersection_area / builing_shp_geom.area
            #         if overlap_percentage >= overlap_threshold:
            #             # if overlap_percentage >= overlap_threshold or overlap_percentage2 >= overlap_threshold:
            #             selected_features.append(segment_feature[1])
            #             break
            #
            #     # 判断是否存在包含关系
            #     if builing_geom.contains(segment_geom):
            #         selected_features.append(segment_feature[1])
            #         break
            #
            #     # 判断是否存在被包含关系
            #     if builing_geom.within(segment_geom):
            #         selected_features.append(segment_feature[1])
            #         break

        # 数据清理：移除无效几何对象
        selected_features = [feature for feature in selected_features if feature.geometry.is_valid]

        # 创建满足阈值的要素的GeoDataFrame
        result = gpd.GeoDataFrame(selected_features, columns=segment_shp_gdf.columns)
        result = result.set_geometry('geometry')

        result.to_file(result_shp_path, driver='ESRI Shapefile')

    @staticmethod
    # 算的不准
    def overlap_segment_result_of_building3(segment_shp_path: str, building_shp_path: str, overlap_threshold: float,
                                            result_shp_path: str) -> str:
        """
        对分割结果shp与建筑物shp进行overlap计算，得到有交集的分割结果新shp

        :param segment_shp_path: 分割结果shp文件路径
        :param building_shp_path: 建筑物shp文件路径
        :param overlap_threshold: 重叠面积百分比的阈值
        :param logger: 日志对象
        :return: 交集后的分割结果shp文件
        """

        # 该算法没有考虑multipolygon相交问题？

        # 分割结果shp文件
        segment_shp_gdf = gpd.read_file(segment_shp_path)

        # 建筑物shp文件
        building_shp_gdf = gpd.read_file(building_shp_path)

        building_shp_spatial_index = building_shp_gdf.sindex

        # 存储满足重叠要求的要素
        selected_features = []

        # 遍历分割结果shp文件的要素
        for segment_feature in segment_shp_gdf.iterrows():
            segment_geom = segment_feature[1].geometry

            segment_geom_bounds = segment_geom.bounds

            # 使用R树索引进行快速空间查询
            intersecting_indices = list(building_shp_spatial_index.intersection(segment_geom_bounds))

            # 判断分割结果shp文件的要素是否与建筑物shp文件的要素有重叠
            for i in intersecting_indices:
                builing_shp_geom = building_shp_gdf.geometry[i]

                # 判断重叠面积百分比是否满足阈值
                intersection_area = segment_geom.intersection(builing_shp_geom).area
                overlap_percentage = intersection_area / segment_geom.area
                # overlap_percentage2 = intersection_area / builing_shp_geom.area
                if overlap_percentage >= overlap_threshold:
                    # if overlap_percentage >= overlap_threshold or overlap_percentage2 >= overlap_threshold:
                    selected_features.append(segment_feature[1])
                    break

            # # 遍历建筑物个shp文件的要素,效率慢
            # for building_feature in building_shp_gdf.iterrows():
            #     builing_geom = building_feature[1].geometry
            #     # 判断是否存在相交关系
            #     if builing_geom.intersects(segment_geom):
            #         # 判断重叠面积百分比是否满足阈值
            #         intersection_area = segment_geom.intersection(builing_geom).area
            #         overlap_percentage = intersection_area / segment_geom.area
            #         # overlap_percentage2 = intersection_area / builing_shp_geom.area
            #         if overlap_percentage >= overlap_threshold:
            #             # if overlap_percentage >= overlap_threshold or overlap_percentage2 >= overlap_threshold:
            #             selected_features.append(segment_feature[1])
            #             break
            #
            #     # 判断是否存在包含关系
            #     if builing_geom.contains(segment_geom):
            #         selected_features.append(segment_feature[1])
            #         break
            #
            #     # 判断是否存在被包含关系
            #     if builing_geom.within(segment_geom):
            #         selected_features.append(segment_feature[1])
            #         break

        # 数据清理：移除无效几何对象
        selected_features = [feature for feature in selected_features if feature.geometry.is_valid]

        # 创建满足阈值的要素的GeoDataFrame
        result = gpd.GeoDataFrame(selected_features, columns=segment_shp_gdf.columns)
        result = result.set_geometry('geometry')

        result.to_file(result_shp_path, driver='ESRI Shapefile')

    @staticmethod
    # 算的不准
    def overlap_segment_result_of_building4(segment_shp_path: str, building_shp_path: str, overlap_threshold: float,
                                            result_shp_path: str) -> str:
        """
        对分割结果shp与建筑物shp进行overlap计算，得到有交集的分割结果新shp

        :param segment_shp_path: 分割结果shp文件路径
        :param building_shp_path: 建筑物shp文件路径
        :param overlap_threshold: 重叠面积百分比的阈值
        :param logger: 日志对象
        :return: 交集后的分割结果shp文件
        """

        # 该算法没有考虑multipolygon相交问题？

        # 分割结果shp文件
        segment_shp_gdf = gpd.read_file(segment_shp_path)

        # 建筑物shp文件
        building_shp_gdf = gpd.read_file(building_shp_path)

        building_shp_spatial_index = building_shp_gdf.sindex

        # 存储满足重叠要求的要素
        selected_features = []

        # 遍历分割结果shp文件的要素
        for segment_feature in segment_shp_gdf.iterrows():
            segment_geom = segment_feature[1].geometry

            # 遍历建筑物个shp文件的要素,效率慢
            for building_feature in building_shp_gdf.iterrows():
                builing_geom = building_feature[1].geometry
                # 判断是否存在相交关系
                if builing_geom.intersects(segment_geom):
                    # 判断重叠面积百分比是否满足阈值
                    intersection_area = segment_geom.intersection(builing_geom).area
                    overlap_percentage = intersection_area / segment_geom.area
                    # overlap_percentage2 = intersection_area / builing_shp_geom.area
                    if overlap_percentage >= overlap_threshold:
                        # if overlap_percentage >= overlap_threshold or overlap_percentage2 >= overlap_threshold:
                        selected_features.append(segment_feature[1])
                        break

                # 判断是否存在包含关系
                if builing_geom.contains(segment_geom):
                    selected_features.append(segment_feature[1])
                    break

                # 判断是否存在被包含关系
                if builing_geom.within(segment_geom):
                    selected_features.append(segment_feature[1])
                    break

        # 数据清理：移除无效几何对象
        selected_features = [feature for feature in selected_features if feature.geometry.is_valid]

        # 创建满足阈值的要素的GeoDataFrame
        result = gpd.GeoDataFrame(selected_features, columns=segment_shp_gdf.columns)
        result = result.set_geometry('geometry')

        result.to_file(result_shp_path, driver='ESRI Shapefile')

    @staticmethod
    def overlap_two_shp(baseShp: str, compareShp: str, overlapShp: str) -> None:
        """
        对两个shp进行重叠分析，保留重叠后的第一个shp的要素

        :param baseShp: 第一个shp
        :param compareShp: 第二个shp
        :param overlapShp: 重叠计算后的新shp
        """
        # 读取第一个shp文件
        gdf1 = gpd.read_file(baseShp)

        # 读取第二个shp文件
        gdf2 = gpd.read_file(compareShp)

        # 创建R树索引
        idx = index.Index()
        for i, geom in enumerate(gdf2.geometry):
            idx.insert(i, geom.bounds)

        # 定义重叠面积百分比的阈值
        overlap_threshold = 0.75

        # 存储满足重叠要求的要素
        selected_features = []

        # 遍历第一个shp文件的要素
        for feature1 in gdf1.iterrows():
            geom1 = feature1[1].geometry
            bounds1 = geom1.bounds

            # 使用R树索引进行快速空间查询
            intersecting_indices = list(idx.intersection(bounds1))

            # 判断第一个shp文件的要素是否与第二个shp文件的要素有重叠
            for i in intersecting_indices:
                geom2 = gdf2.geometry[i]

                # 判断重叠面积百分比是否满足阈值
                intersection_area = geom1.intersection(geom2).area
                overlap_percentage = intersection_area / geom1.area
                if overlap_percentage >= overlap_threshold:
                    selected_features.append(feature1[1])
                    break

        # 创建满足阈值的要素的GeoDataFrame
        result = gpd.GeoDataFrame(selected_features, columns=gdf1.columns)

        # 保存结果为新的shp文件
        result.to_file(overlapShp, driver='ESRI Shapefile')

    @staticmethod
    def is_geom_almost_equals(base_geometry: object, compare_geometry: object, distance_threshold: float) -> bool:
        """
        判断几何空间是否几乎相等，能允许细微的差异

        :param base_geometry : 几何对象
        :param compare_geometry : 比较的几何对象
        :param distance_threshold :距离比较阈值：0.1度-->10公里,0.001度为100米,0.0001度为10米,0.00001度为1米
        :return: 是否相等
        """
        is_almost_equal = False

        # 方法1
        # is_almost_equal= gpd.testing.geom_almost_equals(polygon1, polygon2)

        # 方法2
        # 计算Hausdorff距离
        distance1 = base_geometry.hausdorff_distance(compare_geometry)
        distance2 = compare_geometry.hausdorff_distance(base_geometry)

        # 设置阈值来判断形状变化是否大
        # 0.1度-->10公里,0.001度为100米,0.0001度为10米,0.00001度为1米
        # distance_threshold = 0.0001

        if distance1 > distance_threshold or distance2 > distance_threshold:
            is_almost_equal = False
        else:
            is_almost_equal = True
        return is_almost_equal

    @staticmethod
    def union_two_shp_and_remove_same_feature(shpfile1: str, shpfile2: str, output_shpfile: str) -> None:
        """
        对两个shp要素进行合并并去掉重复要素

        @param shpfile1: 第一个shp文件路径
        @param shpfile2: 第二个shp文件路径
        @param output_shpfile: 合并并去重后的shp文件路径
        """
        # 读取第一个Shapefile文件
        gdf1 = gpd.read_file(shpfile1)

        # 读取第二个Shapefile文件
        gdf2 = gpd.read_file(shpfile2)

        # 合并两个GeoDataFrame
        merged_gdf = gpd.GeoDataFrame(pd.concat([gdf1, gdf2], ignore_index=True), crs=gdf1.crs)
        #
        # # 根据唯一属性值进行合并并保留第一个要素
        # merged_gdf = merged_gdf.dissolve(by='unique_attribute', keep='first')
        # # 执行要素合集并去重
        # merged_gdf = gpd.overlay(gdf1, gdf2, how='union')

        # 去除重复的要素
        merged_gdf = merged_gdf.drop_duplicates(subset=["geometry"], keep='first')

        # 创建新的Shapefile文件来保存合并后的结果
        merged_gdf.to_file(output_shpfile, driver="ESRI Shapefile")

    @staticmethod
    def merge_all_shps(shp_files: list, out_shp: str) -> None:
        """
        对所有的shp进行合并成一个shp

        :param shp_files: 待合并的shp数组
        :param out_shp: 合并的shp
        """
        # 创建一个空的GeoDataFrame来存储所有要素
        merged_gdf = gpd.GeoDataFrame()

        # 遍历所有要合并的SHP文件
        # shp_files = ['path/to/file1.shp', 'path/to/file2.shp', 'path/to/file3.shp']

        for shp_file in shp_files:
            # 读取每个SHP文件的要素
            gdf = gpd.read_file(shp_file)

            # 将要素追加到合并的GeoDataFrame中
            merged_gdf = merged_gdf.append(gdf, ignore_index=True)

        # 保存合并后的SHP文件
        merged_gdf.to_file(out_shp)

    @staticmethod
    def clip_vector_by_shp_expand(buffer_distance: float, clip_shpfile: str, base_shpfile: str,
                                  out_shpfile: str) -> None:

        # 读取第一个 shp 文件
        clip_shp = gpd.read_file(clip_shpfile)

        # 扩展第一个 shp 的空间范围
        expanded_extent = clip_shp.total_bounds
        expanded_extent = box(*expanded_extent).buffer(buffer_distance / 1000 * 0.01)  # 扩展1公里，根据需要调整缓冲区大小
        # expanded_extent = Polygon(expanded_extent).buffer(1000)  # 扩展1公里，根据需要调整缓冲区大小

        # 读取第二个 shp 文件
        base_shp = gpd.read_file(base_shpfile)

        # 裁剪第二个 shp
        clipped_shp = gpd.clip(base_shp, expanded_extent)

        # 保存裁剪后的 shp 文件
        clipped_shp.to_file(out_shpfile)

    @staticmethod
    def get_difference_of_two_building_object(before_building_shp_path: str, after_building_shp_path: str,
                                              result_shp_file_path: str) -> None:
        """
        对两期建筑物识别结果进行差异性分析，得到变化检测结果

        :param before_building_shp_path: 变化前的建筑物矢量shp文件路径
        :param after_building_shp_path: 变化后的建筑物矢量文件路径
        :param logger: 日志对象
        :return: 建筑物变化检测结果shp文件路径
        """
        print("进入get_difference_of_two_building_object")
        print("before_building_shp_path:{}".format(before_building_shp_path))
        print("after_building_shp_path:{}".format(after_building_shp_path))
        print("result_shp_file_path:{}".format(result_shp_file_path))
        # 读取原始建筑物数据
        before_building = gpd.read_file(before_building_shp_path)
        # parser, metadata = get_parser_with_args()
        # opt = parser.parse_args()
        # if opt.is_debug_plot:
        #     CommonOperator.draw_shp_data(before_building, "before_bulding")
        after_building = gpd.read_file(after_building_shp_path)
        # if opt.is_debug_plot:
        #     CommonOperator.draw_shp_data(after_building, "after_building")

        change_features = []

        # 构建建筑物索引
        after_building_spatial_index = after_building.sindex
        before_building_spatial_index = before_building.sindex

        # 遍历变化前的建筑物要素，与变化后建筑物要素，进行变化判断
        for before_building_idx, before_building_row in before_building.iterrows():
            before_building_geom = before_building_row.geometry
            # 判断是否存在相交的建筑物(与外框）
            intersecting_indices = list(after_building_spatial_index.intersection(before_building_geom.bounds))
            intersecting_buildings = after_building.iloc[intersecting_indices]
            # 若框不相交，变化前建筑要素为减少
            if len(intersecting_indices) == 0:
                before_building_row['changeType'] = 'Decreased'
                change_features.append(before_building_row)
            else:
                # 若外框相交，再判断是真相交（框交），还是假相交（要素没有相交）
                # 如果是假相交，则变化前建筑要素为减少
                # 若真相交，再判断是不变（almost equals）,还是改变
                # 交集可能是多个
                change_type = ""
                for intersect_building_idx, intersect_building_row in intersecting_buildings.iterrows():
                    intersect_building_geom = intersect_building_row.geometry
                    # 若是假相交
                    if before_building_geom.disjoint(intersect_building_geom):
                        change_type = 'Decreased'
                    # 真相交
                    else:
                        # 没有改变
                        if ShpFileOperator.is_geom_almost_equals(before_building_geom, intersect_building_geom, 0.0001):
                            # 如果没有改变，则不再循环
                            change_type = 'Not Changed'
                            break
                        # 改变
                        else:
                            change_type = 'Changed'
                before_building_row['changeType'] = change_type
                change_features.append(before_building_row)

        # 遍历变化后的建筑物要素，与变化前建筑物要素，进行变化判断
        for after_building_idx, after_building_row in after_building.iterrows():
            after_building_geom = after_building_row.geometry
            # 判断是否存在相交的建筑物（与外框）
            intersecting_indices = list(before_building_spatial_index.intersection(after_building_geom.bounds))
            # 若框不相交，变化后建筑物要素为增加
            if len(intersecting_indices) == 0:
                after_building_row['changeType'] = 'Increased'
                change_features.append(after_building_row)
            else:
                # 若外框相交，再判断是真相交（框交），还是假相交（要素没有相交）
                # 如果是假相交，则变化后建筑要素为增加
                # 交集可能是多个
                change_type = ""
                for intersect_building_idx, intersect_building_row in intersecting_buildings.iterrows():
                    intersect_building_geom = intersect_building_row.geometry
                    # 若是假相交
                    if after_building_geom.disjoint(intersect_building_geom):
                        change_type = 'Increased'
                    # 真相交
                    else:
                        # 没有改变
                        if ShpFileOperator.is_geom_almost_equals(after_building_geom, intersect_building_geom, 0.0001):
                            # 如果没有改变，则不再循环
                            change_type = 'Not Changed'
                            break
                        # 改变
                        else:
                            change_type = 'Changed'
                if change_type == 'Increased':
                    after_building_row['changeType'] = 'Increased'
                    change_features.append(after_building_row)

        # 创建数据集
        change_building = gpd.GeoDataFrame(change_features)
        # if opt.is_debug_plot:
        #     CommonOperator.draw_shp_data(change_building, "change_building")
        # 最后删除不改变的
        change_building_need = change_building[change_building['changeType'] != 'Not Changed']
        # if opt.is_debug_plot:
        #     CommonOperator.draw_shp_data(change_building_need, "change_building_need")

        # 保存变化结果到新的Shapefile
        change_building_need.to_file(result_shp_file_path)

    @staticmethod
    def get_difference_of_two_building_object2(before_building_shp_path: str, after_building_shp_path: str,
                                               result_shp_file_path: str, intersect_threshold: float) -> None:
        """
        对两期建筑物识别结果进行差异性分析，得到变化检测结果

        :param before_building_shp_path: 变化前的建筑物矢量shp文件路径
        :param after_building_shp_path: 变化后的建筑物矢量文件路径
        :param logger: 日志对象
        :return: 建筑物变化检测结果shp文件路径
        """
        from osgeo import ogr

        # 打开第一个SHP文件
        shp1 = ogr.Open(before_building_shp_path)
        layer1 = shp1.GetLayer(0)

        # 打开第二个SHP文件
        shp2 = ogr.Open(after_building_shp_path)
        layer2 = shp2.GetLayer(0)

        # 创建新的SHP文件
        driver = ogr.GetDriverByName("ESRI Shapefile")
        output_shp = driver.CreateDataSource(result_shp_file_path)
        output_layer = output_shp.CreateLayer("change_analysis", geom_type=ogr.wkbPolygon)

        # 添加属性字段到输出图层
        field_def = ogr.FieldDefn("Change", ogr.OFTString)
        output_layer.CreateField(field_def)

        # 进行变化分析
        for feature1 in layer1:
            geom1 = feature1.GetGeometryRef()
            change = "Not Changed"
            for feature2 in layer2:
                geom2 = feature2.GetGeometryRef()
                if geom1.Intersects(geom2):
                    intersection = geom1.Intersection(geom2)
                    if not intersection.IsEmpty():
                        # 计算相交面积率
                        intersection_area = intersection.GetArea()
                        geometry1_area = geom1.GetArea()
                        intersection_ratio = intersection_area / geometry1_area
                        if intersection_ratio < intersect_threshold:
                            change = "Changed"
                        else:
                            change = "Not Changed"
                        break

            if change != "Not Changed":
                output_feature = ogr.Feature(output_layer.GetLayerDefn())
                output_feature.SetGeometry(geom1.Clone())
                output_feature.SetField("Change", change)
                output_layer.CreateFeature(output_feature)

        for feature2 in layer2:
            geom2 = feature2.GetGeometryRef()
            fid2 = feature2.GetFID()
            change = "Increased"

            for feature1 in layer1:
                geom1 = feature1.GetGeometryRef()
                fid1 = feature1.GetFID()

                if geom2.Intersects(geom1):
                    change = "Not Increased"
                    break

            if change == "Increased":
                output_feature = ogr.Feature(output_layer.GetLayerDefn())
                output_feature.SetGeometry(geom2.Clone())
                output_feature.SetField("Change", change)
                output_layer.CreateFeature(output_feature)

        # 处理要素减少的情况
        for feature1 in layer1:
            geom1 = feature1.GetGeometryRef()
            fid1 = feature1.GetFID()
            change = "Decreased"

            for feature2 in layer2:
                geom2 = feature2.GetGeometryRef()
                fid2 = feature2.GetFID()

                if geom2.Intersects(geom1):
                    change = "Not Decreased"
                    break

            if change == "Decreased":
                output_feature = ogr.Feature(output_layer.GetLayerDefn())
                output_feature.SetGeometry(geom1.Clone())
                output_feature.SetField("Change", change)
                output_layer.CreateFeature(output_feature)

        # 关闭数据源
        shp1 = None
        shp2 = None
        output_shp = None

    @staticmethod
    def remain_overlap_low_feature_of_two_shp(first_shp: str, second_shp: str, low_overlap_ratio: float,
                                              out_shp: str) -> None:
        """
        计算两个shp中不相交，或相交小于指定重叠率的要素，保留第一个shp中满足条件的要素，并生成新的shp

        @param first_shp: 第一个shp
        @param second_shp: 第二个shp
        @param low_overlap_ratio: 指定重叠率
        @param out_shp: 新的shp
        """
        # 加载第一个 shapefile
        first_shapefile = gpd.read_file(first_shp)

        # 加载第二个 shapefile
        second_shapefile = gpd.read_file(second_shp)

        # 找到相交的要素
        intersected_features = gpd.overlay(first_shapefile, second_shapefile, how='intersection')

        # 计算第一个 shapefile 中每个要素的面积
        first_shapefile['area'] = first_shapefile.geometry.area

        # 计算重叠率
        overlap_ratio = intersected_features.geometry.area / first_shapefile.area

        # 保留重叠率小于指定最小重叠率 的要素
        low_overlap_features = first_shapefile[overlap_ratio < low_overlap_ratio]

        # # 计算第一个 shapefile 中不与第二个相交的要素，这个方式用第二个去裁切第一个，保留的是裁切后的要素，不是我们想要的
        # non_intersected_features = gpd.overlay(first_shapefile,second_shapefile, how='difference')
        # 创建 R 树索引
        idx = index.Index()
        for i, second_feature in second_shapefile.iterrows():
            idx.insert(i, second_feature.geometry.bounds)

        non_intersected_features = []

        # 遍历第一个 shapefile 的要素
        for i, first_feature in first_shapefile.iterrows():
            # 获取第一个要素的边界框
            bounds = first_feature.geometry.bounds

            # 使用 R 树索引查找相交的要素
            intersected_indices = list(idx.intersection(bounds))

            # 判断是否有相交的要素
            if len(intersected_indices) == 0:
                non_intersected_features.append(first_feature)
        non_intersected_gpd = gpd.GeoDataFrame(non_intersected_features, columns=first_shapefile.columns)
        non_intersected_gpd.set_geometry('geometry')

        # 最后的结果是 第一个shp里没有相交+第一个shp里相交率很低（低于指定重叠率）
        final_result = low_overlap_features.append(non_intersected_features)

        # 保存结果到新的 shapefile
        final_result.to_file(out_shp)

    @staticmethod
    # 删除shp里的要素, 通过id
    def delete_feature_in_shp_by_ids(input_shp_path, del_id_list):
        # 注册所有驱动
        gdal.AllRegister()
        # 解决中文路径乱码问题
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        driver = ogr.GetDriverByName('ESRI Shapefile')
        origin_pFeatureDataset = driver.Open(input_shp_path, 1)
        origin_pFeaturelayer = origin_pFeatureDataset.GetLayer(0)
        for del_id in del_id_list:
            print("----正在删除要素ID:" + str(del_id))
            origin_pFeaturelayer.DeleteFeature(del_id)
        strSQL = "REPACK " + str(origin_pFeaturelayer.GetName())
        origin_pFeatureDataset.ExecuteSQL(strSQL, None, "")
        origin_pFeaturelayer = None
        origin_pFeatureDataset = None

    @staticmethod
    # 删除shp里的要素,通过where条件
    def delete_feature_in_shp_by_where2(input_shp_path, strFilter):
        # 注册所有驱动
        gdal.AllRegister()
        # 解决中文路径乱码问题
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        driver = ogr.GetDriverByName('ESRI Shapefile')
        origin_pFeatureDataset = driver.Open(input_shp_path, 1)
        origin_pFeaturelayer = origin_pFeatureDataset.GetLayer(0)
        # 按条件查询空间要素，本例查询字段名为Value，字段值为0的所有要素。
        origin_pFeaturelayer.SetAttributeFilter(strFilter)
        for pFeature in origin_pFeaturelayer:
            pFeatureFID = pFeature.GetFID()
            origin_pFeaturelayer.DeleteFeature(int(pFeatureFID))
        strSQL = "REPACK " + str(origin_pFeaturelayer.GetName())
        origin_pFeatureDataset.ExecuteSQL(strSQL, None, "")
        origin_pFeaturelayer = None
        origin_pFeatureDataset = None

    @staticmethod
    # 删除shp里的要素,通过where条件
    def delete_feature_in_shp_by_where(input_shp_path, strFieldName, strFieldType, strFilterValue):
        # 注册所有驱动
        gdal.AllRegister()
        # 解决中文路径乱码问题
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        driver = ogr.GetDriverByName('ESRI Shapefile')
        origin_pFeatureDataset = driver.Open(input_shp_path, 1)
        origin_pFeaturelayer = origin_pFeatureDataset.GetLayer(0)

        # 按条件查询空间要素，本例查询字段名为Value，字段值为0的所有要素。
        fCount = origin_pFeaturelayer.GetFeatureCount()
        for i in range(fCount):
            feature = origin_pFeaturelayer.GetFeature(i)  # 返回图层里索引为index的要素
            code = feature.GetField(strFieldName)
            # 删除要素需要通过FID
            if (code == strFilterValue):
                id = feature.GetFID()
                origin_pFeaturelayer.DeleteFeature(int(id))
        strSQL = "REPACK " + str(origin_pFeaturelayer.GetName())
        origin_pFeatureDataset.ExecuteSQL(strSQL, None, "")
        origin_pFeaturelayer = None
        origin_pFeatureDataset = None

    @staticmethod
    def delete_shp_by_area(shp_path, area_value):

        # 打开Shapefile
        shapefile_path = shp_path
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataset = driver.Open(shapefile_path, 1)  # 1表示以写入模式打开

        # 获取第一个图层
        layer = dataset.GetLayer()

        # 定义删除条件，例如根据面积删除小于某个阈值的图斑
        threshold_area = area_value  # 阈值面积，单位可以根据实际情况调整

        # 遍历图层中的要素
        layer.ResetReading()  # 重置读取位置
        deleted_features = 0  # 记录删除的要素数量
        for feature in layer:
            # 获取要素的面积
            geometry = feature.GetGeometryRef()
            area = geometry.GetArea()  # 获取面积，单位可以根据实际情况调整

            # 根据条件删除要素
            if area < threshold_area:
                layer.DeleteFeature(feature.GetFID())  # 删除要素
                deleted_features += 1

        # 提交修改并关闭数据集
        layer.CommitTransaction()
        dataset = None

        print("删除了 {} 个小图斑".format(deleted_features))

    @staticmethod
    # 获取shp属性数据和空间数据
    def get_shp_record(shp_path):
        # 为了支持中文路径，请添加下面这句代码
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        # 为了使属性表字段支持中文，请添加下面这句
        gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
        # 注册所有的驱动
        ogr.RegisterAll()

        ds = ogr.Open(shp_path, 0)
        layer = ds.GetLayer(0)

        lydefn = layer.GetLayerDefn()
        spatialref = layer.GetSpatialRef()
        # spatialref.ExportToProj4()
        # spatialref.ExportToWkt()
        geomtype = lydefn.GetGeomType()
        fieldlist = []
        for i in range(lydefn.GetFieldCount()):
            fddefn = lydefn.GetFieldDefn(i)
            fddict = {'name': fddefn.GetName(), 'type': fddefn.GetType(),
                      'width': fddefn.GetWidth(), 'decimal': fddefn.GetPrecision()}
            fieldlist += [fddict]
        # records
        geomlist = []
        reclist = []
        feature = layer.GetNextFeature()
        while feature is not None:
            geom = feature.GetGeometryRef()
            geomlist += [geom.ExportToWkt()]
            rec = {}
            for fd in fieldlist:
                rec[fd['name']] = feature.GetFieldAsString(fd['name'])
            reclist += [rec]
            feature = layer.GetNextFeature()
        # close
        ds.Destroy()
        return geomlist, reclist

    @staticmethod
    # 获取图层的空间范围
    def get_layer_envlope(shp_path):
        ds = ogr.Open(shp_path, True)  # True表示以读写方式打开
        layer = ds.GetLayer(0)
        left, right, down, up = layer.GetExtent()
        return left, right, down, up

    @staticmethod
    # 获取要素的空间范围
    def get_feature_envlope(shp_path):
        ds = ogr.Open(shp_path, True)  # True表示以读写方式打开
        layer = ds.GetLayer(0)
        fCount = layer.GetFeatureCount()
        reslut_list = []
        for index in range(fCount):
            feature = layer.GetFeature(index)
            geom = feature.GetGeometryRef()
            # left,right,down,up表示shp里一个要素的边界，即左经度、右经度、下纬度、上纬度
            left, right, down, up = geom.GetEnvelope()
            reslut_list.append(left, right, down, up)
        return reslut_list

    @staticmethod
    def get_envlope_of_shp(shp_path: str, out_shp: str) -> None:
        import geopandas as gpd
        from shapely.geometry import Polygon

        # 读取Shapefile文件
        input_shapefile = shp_path
        data = gpd.read_file(input_shapefile)

        # 创建新的多边形集合
        polygons = []
        for index, row in data.iterrows():
            envelope = row.geometry.envelope
            polygons.append(Polygon(envelope.exterior.coords))

        # 创建新的GeoDataFrame来保存多边形
        poly_data = gpd.GeoDataFrame(geometry=polygons)

        # 保存为新的Shapefile文件
        output_shapefile = out_shp
        poly_data.to_file(output_shapefile)

    @staticmethod
    def convert_multiplygon_to_polygon(shp_path: str, out_shp: str) -> None:
        from osgeo import ogr

        # 打开原始 SHP 文件
        shp = ogr.Open(shp_path)
        layer = shp.GetLayer()

        # 创建输出 SHP 文件
        driver = ogr.GetDriverByName('ESRI Shapefile')
        output_shp = driver.CreateDataSource(out_shp)
        output_layer = output_shp.CreateLayer('output', geom_type=ogr.wkbPolygon)

        # 从原始 SHP 文件中复制属性字段到输出 SHP 文件
        feature_defn = layer.GetLayerDefn()
        for i in range(feature_defn.GetFieldCount()):
            output_layer.CreateField(feature_defn.GetFieldDefn(i))

        # 遍历原始 SHP 文件的要素
        for feature in layer:
            geom = feature.GetGeometryRef()

            # 如果要素为多边形类型
            if geom.GetGeometryType() == ogr.wkbPolygon:
                output_feature = ogr.Feature(feature_defn)

                # 单个多边形要素直接保存
                output_feature.SetGeometry(geom)

                # 复制属性值到输出 SHP 文件
                for i in range(feature_defn.GetFieldCount()):
                    output_feature.SetField(i, feature.GetField(i))

                # 将要素添加到输出图层
                output_layer.CreateFeature(output_feature)

            # 如果要素为多边形集合类型
            elif geom.GetGeometryType() == ogr.wkbMultiPolygon:
                # 遍历多边形集合的每个多边形
                for i in range(geom.GetGeometryCount()):
                    polygon = geom.GetGeometryRef(i)

                    output_feature = ogr.Feature(feature_defn)

                    # 单个多边形要素直接保存
                    output_feature.SetGeometry(polygon)

                    # 复制属性值到输出 SHP 文件
                    for i in range(feature_defn.GetFieldCount()):
                        output_feature.SetField(i, feature.GetField(i))

                    # 将要素添加到输出图层
                    output_layer.CreateFeature(output_feature)

        # 关闭数据源
        shp = None
        output_shp = None

    @staticmethod
    # 将shp进行上下翻转
    def updown_reverse_shp(input_shp_path):
        # 注册所有驱动
        gdal.AllRegister()
        # 解决中文路径乱码问题
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        gdal.SetConfigOption("SHAPE_ENCODING", "")
        driver = ogr.GetDriverByName('ESRI Shapefile')
        origin_pFeatureDataset = driver.Open(input_shp_path, 1)
        origin_pFeaturelayer = origin_pFeatureDataset.GetLayer(0)
        origin_featureLayerNum = origin_pFeaturelayer.GetFeatureCount(0)
        layer_minY = origin_pFeaturelayer.GetExtent()[2]
        layer_maxY = origin_pFeaturelayer.GetExtent()[3]
        # 获取要素
        for t in range(0, origin_featureLayerNum):
            origin_ofeature = origin_pFeaturelayer.GetFeature(t)
            origin_geom = origin_ofeature.GetGeometryRef()
            reverse_geom = ShpFileOperator.handle_reverse_geomety(origin_geom, layer_minY, layer_maxY)
            origin_ofeature.SetGeometry(reverse_geom)
            origin_pFeaturelayer.SetFeature(origin_ofeature)
        origin_pFeaturelayer = None
        origin_pFeatureDataset = None

    @staticmethod
    def handle_reverse_geomety(origin_geom, minY, maxY):
        # minY = origin_geom.GetEnvelope()[2]
        # maxY = origin_geom.GetEnvelope()[3]
        offsetY = abs(maxY - minY)
        origin_geom_wkt = origin_geom.ExportToWkt()
        point_list = origin_geom_wkt.lstrip("'POLYGON ((").rstrip("))'").split(",")
        point1_x = float(point_list[0].split(" ")[0])
        point1_y = minY + (offsetY - (float(point_list[0].split(" ")[1]) - minY))
        point2_x = float(point_list[1].split(" ")[0])
        point2_y = minY + (offsetY - (float(point_list[1].split(" ")[1]) - minY))
        point3_x = float(point_list[2].split(" ")[0])
        point3_y = minY + (offsetY - (float(point_list[2].split(" ")[1]) - minY))
        point4_x = float(point_list[3].split(" ")[0])
        point4_y = minY + (offsetY - (float(point_list[3].split(" ")[1]) - minY))
        reverse_geom_wkt = "POLYGON((%f %f,%f %f,%f %f,%f %f,%f %f))" % (
            point1_x, point1_y, point2_x, point2_y, point3_x, point3_y, point4_x, point4_y, point1_x, point1_y)
        return ogr.CreateGeometryFromWkt(reverse_geom_wkt)


    @staticmethod
    # 删除小于阈值的shp图斑
    def delete_shp_by_area(shp_path, area_value):
        # 打开Shapefile
        shapefile_path = shp_path
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataset = driver.Open(shapefile_path, 1)  # 1表示以写入模式打开

        # 获取第一个图层
        layer = dataset.GetLayer()

        # 定义删除条件，例如根据面积删除小于某个阈值的图斑
        threshold_area = area_value  # 阈值面积，单位可以根据实际情况调整

        # 遍历图层中的要素
        layer.ResetReading()  # 重置读取位置
        deleted_features = 0  # 记录删除的要素数量
        for feature in layer:
            # 获取要素的面积
            geometry = feature.GetGeometryRef()
            area = geometry.GetArea()  # 获取面积，单位可以根据实际情况调整

            # 根据条件删除要素
            if area < threshold_area:
                layer.DeleteFeature(feature.GetFID())  # 删除要素
                deleted_features += 1

        # 提交修改并关闭数据集
        layer.CommitTransaction()
        dataset = None

        print("删除了 {} 个小图斑".format(deleted_features))

    @staticmethod
    # 复制shapefile
    def copy_shape(origin_shp_path):
        (file_pre_path, temp_filename) = os.path.split(origin_shp_path)
        fname, ext = os.path.splitext(origin_shp_path)
        base_name = os.path.basename(fname)
        origin_file_path_list = []
        dest_file_path_list = []
        origin_file_path_list.append(os.path.join(file_pre_path, base_name + ".shp"))
        dest_file_path_list.append(os.path.join(file_pre_path, base_name + "_copy.shp"))
        origin_file_path_list.append(os.path.join(file_pre_path, base_name + ".shx"))
        dest_file_path_list.append(os.path.join(file_pre_path, base_name + "_copy.shx"))
        origin_file_path_list.append(os.path.join(file_pre_path, base_name + ".prj"))
        dest_file_path_list.append(os.path.join(file_pre_path, base_name + "_copy.prj"))
        origin_file_path_list.append(os.path.join(file_pre_path, base_name + ".dbf"))
        dest_file_path_list.append(os.path.join(file_pre_path, base_name + "_copy.dbf"))
        for i in range(len(origin_file_path_list)):
            copyfile(origin_file_path_list[i], dest_file_path_list[i])
        # 注册所有驱动
        gdal.AllRegister()
        # 解决中文路径乱码问题
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        driver = ogr.GetDriverByName('ESRI Shapefile')
        pFeatureDataset = driver.Open(os.path.join(file_pre_path, base_name + ".shp"), 1)
        return pFeatureDataset

if __name__ == '__main__':
    # 测试栅格转矢量
    # # 边缘会产生很多碎的小图斑（合并后的mask大图）,不能为jpg
    # image_path = "E:\\data\mask\\total_mask_862eb8d9-4be1-4c0e-9959-4e0c16b891f8_binary.jpg"
    # # 边缘没有碎斑
    # image_path = "E:\\data\mask\\69cdda8d-73d7-4b45-b0c5-52b6ec3b3532_6_mask_b0d15bb5-b441-4b23-8441-0b35929c91ad_binary.png"
    # # 边缘没有碎斑
    # image_path="E:\\data\mask\\TW2015_4326_XIAO_MORE2_mask_3dbe10b6-2f7a-4684-a2de-c760565fd803_binary.png"
    # image_path = "E:\\data\mask\\TW2015_4326_XIAO_MORE2_mask_binary.png"
    # img_tranform = []
    # shp_path = "E:\\data\mask\\total_mask_862eb8d9-4be1-4c0e-9959-4e0c16b891f8_binary4.shp"
    # shp_path = "E:\\data\mask\\69cdda8d-73d7-4b45-b0c5-52b6ec3b3532_6_mask_b0d15bb5-b441-4b23-8441-0b35929c91ad_binary.shp"
    # shp_path = "E:\\data\mask\\TW2015_4326_XIAO_MORE2_mask_3dbe10b6-2f7a-4684-a2de-c760565fd803_binary.shp"
    # shp_path = "E:\\data\mask\\TW2015_4326_XIAO_MORE2_mask_binary3.shp"
    # img_tranform = [120.2798363031, 0.0000051526, 0, 22.7289960960, 0, -0.0000051526]
    #
    # ShpFileOperator.raster_to_vector(image_path, img_tranform, shp_path, "ESRI Shapefile")
    # ShpFileOperator.delete_feature_in_shp_by_where2(shp_path, "value!=255")
    # print("ok")

    # 测试多边形接边
    # shp_path = "C:\\Users\\Administrator\\Downloads\\convert_by_mask (5)\\total_mask_591ff2e3-bbb5-484f-a768-a37d7a7ec873_binary.shp"
    # join_shp_path = "C:\\Users\\Administrator\\Downloads\\convert_by_mask (5)\\total_mask_591ff2e3-bbb5-484f-a768-a37d7a7ec873_binary_join_edge5.shp"
    # ShpFileOperator.join_edge_polygon(shp_path, join_shp_path, 0)

    # 测试两个shp多边形找差异

    # building_before_path = "E:\\dong\meta_sam_change_detect\\shp\\remove_non_building\\TW2015_4326_XIAO_MORE2_55c369d7-087b-4fc1-a728-05492e36255c_remove_non_building.shp"
    # building_after_path = "E:\\dong\\meta_sam_change_detect\shp\\remove_non_building\\TW2021_4326_XIAO_MORE2_639ceb32-c8f9-4646-8f0a-9284c5bbd824_remove_non_building.shp"
    # shp_save_path = "E:\\data\\change\\change_result1-1.shp"
    # # ShpFileOperator.get_difference_of_two_building_object(building_before_path, building_after_path, shp_save_path)
    # shp_save_path = "E:\\data\\change\\change_result2-10.shp"
    # # 0.1度-->10公里,0.001度为100米,0.0001度为10米,0.00001度为1米
    # # distance_threshold = 0.0001
    # ShpFileOperator.get_difference_of_two_building_object2(building_before_path, building_after_path, shp_save_path,
    #                                                        0.1)

    # # 测试 正样本过滤
    # segment_shp_path = "E:\\dong\meta_sam_change_detect\\test_data\\convert_by_mask\\TW2015_4326_XIAO_MORE2_55c369d7-087b-4fc1-a728-05492e36255c_mask_binary.shp"
    # # segment_shp_path2 = "E:\\dong\meta_sam_change_detect\\test_data\\convert_by_mask\\TW2015_4326_XIAO_MORE2_55c369d7-087b-4fc1-a728-05492e36255c_mask_binary2.shp"
    # # ShpFileOperator.convert_multiplygon_to_polygon(segment_shp_path, segment_shp_path2)
    # building_shp_path = "E:\\dong\meta_sam_change_detect\\shp\\clip_build_base\\TW2015_4326_XIAO_MORE2_55c369d7-087b-4fc1-a728-05492e36255c_building_base_clip.shp"
    # out_shp_path = "E:\\data\\overlap\\positive_overlap_result6.shp"
    # ShpFileOperator.overlap_segment_result_of_building2(segment_shp_path, building_shp_path, 0, out_shp_path)

    # 测试 负样本过滤
    # first_shp = "E:\\dong\\meta_sam_change_detect\\shp\\union_building_recog\\TW2015_4326_XIAO_MORE2_55c369d7-087b-4fc1-a728-05492e36255c_union_building_recog.shp"
    # second_shp = "E:\\dong\\meta_sam_change_detect\\auxiliary\\non-building\gis_non_buildings_2015.shp"
    # out_shp_path = "E:\\data\\overlap\\negative_overlap_result1.shp"
    # ShpFileOperator.remain_overlap_low_feature_of_two_shp(first_shp, second_shp, 0.1, out_shp_path)
    # out_shp_path = "E:\\data\\overlap\\negative_overlap_result2.shp"
    # ShpFileOperator.remain_overlap_low_feature_of_two_shp2(first_shp, second_shp, 0.1, out_shp_path)

    # 生成shp的envelop的shp
    # input_shp = r"E:\\dong\\变化检测测试数据\\Export_Output_4.shp"
    # out_shp = r"E:\\data\\change\\change_box.shp"
    # ShpFileOperator.get_envlope_of_shp(input_shp, out_shp)

    # 删除小图斑
    shp_path = "E:\\dong\\meta_sam_change_detect\\shp\\change_result\\rs15_3cc4ba65-e7b2-4963-b805-745ecac3eadd_ai_extract_change_resultCopy2.shp"
    ShpFileOperator.delete_shp_by_area(shp_path, 0.0000005)

