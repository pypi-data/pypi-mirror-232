longmao-point-cloud-converter
==================
点云文件转换工具类(pcd,pot)


安装
----------------
.. code-block:: Python

    pip install npccp


使用
----------------
.. code-block:: python

    import npccp

    ############ 工具类
    ## 1. pcd格式转换(ascii,binary,binary_compressed)
    npccp.pcdtopcd(sourcePcd, targetPcd, targetDataType)
    ## 2. pcd转pot(只转换x,y,z,intensity)
    npccp.pcdtopot(pcd, pot)

    ############ 自行封装
    ## 1. pcd读
    with PcdReader(pcd) as reader:
        header = reader.getHeader()
        while True:
            point = reader.getPoint()
            if point is None:
                break
            print(point)
    ## 2. pcd写
    header = PcdXyziHeader()
    header.data = PcdHeader.DATA_TYPE_ASCII
    with PcdWriter(target, header) as writer:
        point = [x,y,z,i]
        writer.write(point) ## 循环写点

    ## 3. pot写
    with PotreeWriter(pot) as writer:
        point = npccp.new_potree_point(x, y, z, intensity, r, g, b)
        writer.write(point) ## 循环写点