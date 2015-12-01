require 'net/http'
require 'json'

`rm ~/interim/*.jpeg`
`rm ~/*.jpeg`

uri = URI(ENV['DOCUMENT_API_URI'] || 'http://localhost:5014')
http = Net::HTTP.new(uri.host, uri.port)
response = http.request(Net::HTTP::Delete.new('/documents'))
