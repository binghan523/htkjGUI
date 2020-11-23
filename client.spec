# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Client.py'],
             pathex=['c:\\users\\qq154\\.virtualenvs\\htkjproject-9axzgckk\\lib\\site-packages', 'E:\\PyCharm 2019.1.2\\pycharmprojects\\htkjproject', 'C:\\Users\\qq154\\.virtualenvs\\htkjproject-9aXzGckk\\Lib\site-packages\\PyQt5\\Qt\\plugins\\platforms'],
             binaries=[('C:\\Users\\qq154\\.virtualenvs\\htkjproject-9aXzGckk\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\platforms\\qwindows.dll', 'qwindows.dll')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
