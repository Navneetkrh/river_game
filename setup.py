import platform
from cx_Freeze import setup, Executable

name = 'jumpy.exe' if platform.system() == 'Windows' else 'jumpy'

buildOptions = dict(
    packages = ['imgui', 'numpy', 'pygame', 'PIL', 'OpenGL'],
    excludes = [],
    include_files = [
        'asset_maker/',
        'assets/',
        'saves/',
        'river_biome/',
        'space_biome/',
        'squid_biome/',
        'utils/',
        'player.json',
        'shapes.json'
    ]
)

base = 'Win32GUI' if platform.system() == 'Windows' else None

executables = [
    Executable('main.py',
        base=base,
        target_name=name,
        icon='assets/textures/water/0000.ico')
]

setup(name='jumpy',
      version = '1.0',
      description = 'river crossing game',
      options = dict(build_exe = buildOptions),
      executables = executables)