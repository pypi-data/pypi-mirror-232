from loguru import logger
import time
import os
from AutoTransferMachine.utils.uploader.upload_tools import *
import re
import cloudscraper

def mangguo_upload(siteinfo,file1,record_path,qbinfo,basic,hashlist):
    url = siteinfo.url
    post_url = f"{url}takeupload.php"
    tags=[]
    time_out=40
    if (file1.pathinfo.type=='anime' or file1.pathinfo.type=='tv') and file1.pathinfo.collection==0:
        fileinfo=file1.chinesename+'在'+siteinfo.sitename+'第'+file1.episodename+'集'
    else:
        fileinfo=file1.chinesename+'在'+siteinfo.sitename


    #选择类型
    if 'anime' in file1.pathinfo.type.lower():
        select_type='405'       
        logger.info('已成功填写类型为动漫')
    elif 'show' in file1.pathinfo.type.lower():
        select_type='403'
        logger.info('已成功填写类型为综艺')                  
    elif 'tv' in file1.pathinfo.type.lower():
        select_type='402'
        logger.info('已成功填写类型为剧集')          
    elif 'movie' in file1.pathinfo.type.lower():
        select_type='401'
        logger.info('已成功填写类型为电影')                  
    elif 'doc' in file1.pathinfo.type.lower():
        select_type='404'
        logger.info('已成功填写类型为纪录片')          
    elif 'mv' in file1.pathinfo.type.lower():
        select_type='406'
        logger.info('已成功填写类型为音乐')          
    elif 'sport' in file1.pathinfo.type.lower():
        select_type='407'
        logger.info('已成功填写类型为学习')          
    elif 'music' in file1.pathinfo.type.lower():
        select_type='409'
        logger.info('已成功填写类型为电子书')          
    else:
        select_type='410'
        logger.info('已成功填写类型为其它')          
        




    #选择来源
    if 'WEB' in file1.pathinfo.source.upper():
        source_sel='7'
        logger.info('已成功选择来源为WEB-DL')          
    elif 'UHD' in file1.pathinfo.source.upper():
        source_sel='1'
        logger.info('已成功选择来源为UHD-BLURAY')         
    elif 'BLU' in file1.pathinfo.source.upper():
        source_sel='1'
        logger.info('已成功选择来源为BLURAY')         
    elif 'ENCODE' in file1.pathinfo.source.upper():
        source_sel='6'
        logger.info('已成功选择来源为ENCODE')         
    elif 'HDTV' in file1.pathinfo.source.upper():
        source_sel='4'
        logger.info('已成功选择来源为HDTV')         
    elif 'REMUX' in file1.pathinfo.source.upper():
        source_sel='6'
        logger.info('已成功选择来源为REMUX')
    elif 'HD' in file1.pathinfo.source.upper() and 'DVD' in file1.pathinfo.source.upper():
        source_sel='2'
        logger.info('已成功选择来源为HD DVD')
    elif 'DVD' in file1.pathinfo.source.upper():
        source_sel='3'
        logger.info('已成功选择来源为DVD')
    elif 'SACD' in file1.pathinfo.source.upper():
        source_sel='9'
        logger.info('已成功选择来源为SACD') 
    elif 'CD' in file1.pathinfo.source.upper():
        source_sel='8'
        logger.info('已成功选择来源为CD')      
    else:
        source_sel='6'
        logger.info('已成功选择来源为其它') 


    
    if siteinfo.uplver==1:
        uplver='yes'
    else:
        uplver='no'

    torrent_file = file1.torrentpath
    file_tup = ("file", (os.path.basename(torrent_file), open(torrent_file, 'rb'), 'application/x-bittorrent')),
            

    other_data = {
            "name": file1.uploadname,
            "small_descr": file1.small_descr+file1.pathinfo.exinfo,
            "url": file1.imdburl,
            "pt_gen": file1.doubanurl,
            "color": "0",
            "font": "0",
            "size": "0",
            "descr": file1.content,
            "type": select_type,
            "source_sel[4]": source_sel,
            "uplver": uplver,
            }

    scraper=cloudscraper.create_scraper()
    success_upload=0
    try_upload=0
    while success_upload==0:
        try_upload+=1
        if try_upload>5:
            return False,fileinfo+' 发布种子发生请求错误,请确认站点是否正常运行'
        logger.info('正在发布种子')
        try:
            r = scraper.post(post_url, cookies=cookies_raw2jar(siteinfo.cookie),data=other_data, files=file_tup,timeout=time_out)
            success_upload=1
        except Exception as r:
            logger.warning('发布种子发生错误: %s' %(r))
            success_upload=0
    
    return afterupload(r,fileinfo,record_path,siteinfo,file1,qbinfo,hashlist)