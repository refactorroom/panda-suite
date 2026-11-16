#!/usr/bin/env node
'use strict';
const path = require('node:path');
const os = require('node:os');

function parse(args) {
  if (args.length === 1 && ['--help', '-h'].includes(args[0])) return { help: true };
  const command = args.shift();
  if (!['install', 'update'].includes(command)) throw Error('Expected install or update. Use --help for usage.');
  const options = { command, destination: path.join(os.homedir(), '.agents', 'skills'), names: [], all: false };
  let destinationSeen = false;
  while (args.length) {
    const arg = args.shift();
    if (arg === '--all' && command === 'install' && !options.all) options.all = true;
    else if (arg === '--skill' && command === 'install') {
      if (!args.length || args[0].startsWith('--')) throw Error('--skill requires a name');
      options.names.push(args.shift());
    } else if (arg === '--destination' && !destinationSeen) {
      if (!args.length || !args[0] || args[0].startsWith('--')) throw Error('--destination requires a path');
      options.destination = path.resolve(args.shift()); destinationSeen = true;
    } else throw Error(`Unknown or repeated option: ${arg}`);
  }
  if (command === 'install' && options.all === (options.names.length > 0)) throw Error('Select exactly one of --all or --skill <name>');
  return options;
}
try {
  const options = parse(process.argv.slice(2));
  if (options.help) console.log('Usage: panda-suite install (--all | --skill <name> ...) [--destination <path>]\n       panda-suite update [--destination <path>]');
  else require('./operations.js').run(options);
} catch (error) { console.error(`panda-suite: ${error.message}`); process.exitCode = 1; }
