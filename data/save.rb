if ARGV.length > 0
    folder = ARGV[0]
else
    abort('No directory')
end

`rm #{folder}/data/*.jpeg`
`cp ~/*.jpeg #{folder}/data/`
