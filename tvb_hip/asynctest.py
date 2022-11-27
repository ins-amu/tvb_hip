"""
Some async stuff for workflow support.  This has to work in the notebook however. 

"""

# TODO test from notebook

import asyncio

async def a(input):
    print('a.started', input)
    proc = await asyncio.create_subprocess_shell('sleep 5')
    await proc.wait()
    print('a.done with ', input)
    return 'done.' + input + '.a'

async def b(input):
    print('b.started', input)
    proc = await asyncio.create_subprocess_shell('sleep 5')
    await proc.wait()
    print('b.done with ', input)
    return 'done.' + input + '.b'

async def c():
    oa, ob = await asyncio.gather(a('c1'), b('c2'))
    await asyncio.create_subprocess_shell('echo %s %s' % (oa, ob))
    return 'done.c'

async def main():
    await c()

if __name__ == '__main__':
    asyncio.run(main())
