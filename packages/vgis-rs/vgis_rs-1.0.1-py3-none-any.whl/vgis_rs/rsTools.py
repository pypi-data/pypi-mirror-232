#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2022/10/28 18:51
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : rsTools.py
# @Descr   : 
# @Software: PyCharm
import os

from osgeo import gdal
from osgeo import osr


class RsToolsOperatoer:
    # 初始化
    def __init__(self, wms_server):
        pass

    @staticmethod
    def get_Env_Tif(tif_path):
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  # 支持中文路径
        dataset = gdal.Open(tif_path)  # 打开tif
        adfGeoTransform = dataset.GetGeoTransform()  # 读取tif的六参数

        iXSize = dataset.RasterXSize  # 列数
        iYSize = dataset.RasterYSize  # 行数

        # 左上角
        tif_minx = adfGeoTransform[0]
        tif_maxy = adfGeoTransform[3]
        # 右下角
        tif_maxx = adfGeoTransform[0] + iXSize * adfGeoTransform[1] + iYSize * adfGeoTransform[2]
        tif_miny = adfGeoTransform[3] + iXSize * adfGeoTransform[4] + iYSize * adfGeoTransform[5]
        return tif_minx, tif_miny, tif_maxx, tif_maxy

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
    def convert_jpg_to_tif(input_jpg_file, out_tif_file):

        # 输入和输出文件路径
        input_file = input_jpg_file
        output_file = out_tif_file

        # 打开JPEG文件
        jpeg_dataset = gdal.Open(input_file)

        # 获取JPEG文件的宽度、高度和波段数
        width = jpeg_dataset.RasterXSize
        height = jpeg_dataset.RasterYSize
        band_count = jpeg_dataset.RasterCount

        # 创建TIFF文件
        driver = gdal.GetDriverByName('GTiff')
        tiff_dataset = driver.Create(output_file, width, height, band_count, gdal.GDT_Byte)

        # 将JPEG文件的内容复制到TIFF文件中
        for i in range(1, band_count + 1):
            band = jpeg_dataset.GetRasterBand(i)
            data = band.ReadAsArray()
            tiff_dataset.GetRasterBand(i).WriteArray(data)

        # 设置TIFF文件的投影和地理转换信息（可选）
        file_pre_path, file_name = os.path.split(input_jpg_file)
        shotname, _ = os.path.splitext(file_name)
        jgw_file_path = os.path.join(file_pre_path, "{}.jgw".format(shotname))
        src_transform = RsToolsOperatoer.convert_jgw_to_gdaltransform(jgw_file_path)

        # 自定义坐标系
        if jpeg_dataset.GetProjection() is None:
            # 如果输入的栅格数据没有地理信息的话，需要自定义坐标系，否则矢量化结果与原数据程垂直镜像对称
            spatial_reference = osr.SpatialReference()
            spatial_reference.ImportFromEPSG(4326)  # WGS84地理坐标系
            jpeg_dataset.SetProjection(spatial_reference.ExportToWkt())
        if jpeg_dataset.GetGeoTransform() is None:
            # 坐标信息
            # 左上角点坐标X
            # x方向的分辨
            # 旋转系数，如果为0，就是标准的正北向图像
            # 左上角点坐标Y
            # 旋转系数，如果为0，就是标准的正北向图像
            # Y方向的分辨率
            # padf_transform = [114.0, 0.000001, 0, 34.0, 0, -0.000001]
            jpeg_dataset.SetGeoTransform(src_transform)

        tiff_dataset.SetProjection(jpeg_dataset.GetProjection())
        tiff_dataset.SetGeoTransform(jpeg_dataset.GetGeoTransform())

        # 关闭文件
        jpeg_dataset = None
        tiff_dataset = None
