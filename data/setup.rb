
if ARGV.length > 0
    folder = ARGV[0]
else
    abort('No directory')
end

`cp #{folder}/data/*.jpeg ~/`
