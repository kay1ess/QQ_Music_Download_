# QQ_Music_Download_
qq音乐下载 爬虫练习
1. 使用request和re bs4等库 对qq 音乐页面 歌曲id 歌曲详情页 歌曲专辑 歌手 信息进行爬取
2. 由于网页使用了动态的vkey 无法直接获取到url下载链接， 使用selenium + headless chrome 模拟浏览器 进行歌曲试听，获取到歌曲的播放url，也就是下载链接
3. 使用Pyqt5 构造GUI 
4. pyqt5 使用了tablewidget控件 将获取到的歌曲信息进行填充 
5. 添加每首歌的下载button 点击button调用 selenium函数 提取到下载链接
6. 加入QfileDialog 进行下载路径选择
