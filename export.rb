require 'json'
require 'csv'
require 'time'

files = Dir['/home/hasi/key_cash/*.log']

logs = []

for file in files
  name = File.basename(file, '.log')
  # Skip the current day
  next if name == Time.now.strftime('%d-%m-%y')

  time = Time.strptime(name, '%d-%m-%y')
  json = JSON.parse(File.open(file).read)
  
  # Add millisecond timestamp
  json['timestamp'] = (time.to_f * 1000).to_i
  
  logs.push json
end

logs.sort! { |x,y| x['timestamp'] <=> y['timestamp']}

keys = logs.last.keys.sort!

sorted_logs = []

for log in logs
  sorted_log = {}
  for key in keys
    sorted_log[key] = log[key] || 0
  end
  sorted_logs.push(sorted_log)
end

csv_string = CSV.open('log.csv', 'wb')  do |csv|
  csv << keys
  for hash in sorted_logs 
    csv << hash.values
  end
end

