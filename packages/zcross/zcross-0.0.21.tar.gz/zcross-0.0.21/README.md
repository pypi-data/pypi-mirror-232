# ZCross

ZCross is a python library used to read low pressure gas sections from various sources like [LXCat](https://lxcat.net/home/).

## Installation

To install this package just use pip:
``` shell
pip install zcross
```

Cross section databases are not provided by `ZCross`: however, it is possible to download the cross section tables of interest from the [download section](https://nl.lxcat.net/data/download.php) of [LXCat](https:://www.lxcat.net).
Once you download the cross sections in `XML` format, you can save it somewhere (we suggest under `/opt/zcross_data`) and to define an enviroment variable pointing to that path:
``` bash
export ZCROSS_DATA=/opt/zcross_data
```
(you can add it to your `.profile` file)

## Examples

List the database availables:
``` python
import zcross

zs = zcross.load_all()
# be patient, it will take a while ...

for z in zs:
	print(z.database)
```
		
Show the groups and references of a speficic database:
``` python
import zcross

z = zcross.load_by_name('ccc')

for group in z.database:
	print(group)

for reference in z.database.references:
	print('[{}]:'.format(reference.type))
	for k,v in reference.items():
	   print('  {:<10} : {}'.format(k,v))
```
		
Show the process of a specific group:
``` python
import zcross

z = zcross.load_by_name('itikawa')

group      = z.database[0]

for process in group:
	print("Process {}: {}".format(process.id, process.get_simple_type()))
	print("Comment: {}\n".format(process.comment))
```
	
Show the cross section table of a specific process:
``` python
import zcross

z = zcross.load_by_name('phelps')

process    = z.database['H2O'][5]

print('Reaction:')
print(process.get_reaction())

print('Energy [{}],\tArea [{}]'.format(process.energy_units, process.cross_section_units))

for energy, area in process:
	print('{:8.2f}\t{:e}'.format(energy, area))
```
