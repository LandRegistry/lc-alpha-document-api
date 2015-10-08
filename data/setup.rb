
if ARGV.length > 0
    folder = ARGV[0]
else
    abort('No directory')
end

['img30_1.jpeg', 'img32_1.jpeg', 'img34_1.jpeg', 'img36_1.jpeg', 'img38_1.jpeg',
'img31_1.jpeg', 'img33_1.jpeg', 'img35_1.jpeg', 'img37_1.jpeg', 'img39_1.jpeg', 'img40_1.jpeg',
'img41_1.jpeg', 'img41_2.jpeg', 'img42_1.jpeg', 'img43_1.jpeg', 'img44_1.jpeg', 'img44_2.jpeg',
'img45_1.jpeg', 'img45_2.jpeg', 'img51_1.jpeg', 'img52_1.jpeg', 'img53_1.jpeg', 'img54_1.jpeg',
'img55_1.jpeg', 'img56_1.jpeg'].each do |image|
    `cp #{folder}/data/#{image} ~/#{image}`
end