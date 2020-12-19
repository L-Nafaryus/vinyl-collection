import HTTP, JSON, CSV, DataFrames

struct Resp
    status
end

function delayedRequest(url, seconds)
    sleep(seconds)
    req = Any

    try
        global req = HTTP.request("GET", url)
    catch
        println(string("[ 404 ] ", url))

        #return Resp(404)
    end

    headers = Dict(req.headers)
        
    if headers["X-Discogs-Ratelimit-Remaining"] == "0"
        println("[ ratelimit ] Waiting for 60 seconds")
        sleep(60)
        
        try
            global req = HTTP.request("GET", url)
        catch
            println(string("[ 404 ] ", url))
        end
    end
        
    println(string("[ ", req.status, " ] ", url))

    return req
end


path = joinpath(pwd(), "build")
data = DataFrames.DataFrame()
#headers = Dict()

isdir(path) || mkdir(path)

if !isfile(joinpath(path, "releases.csv"))
    user = "L-Nafaryus"
    per_page = 300
    releases = []
    
    
    local url = string("https://api.discogs.com/users/", user, "/collection/folders/0/releases?per_page=", per_page)
    local req = delayedRequest(url, 1)
    local body = JSON.parse(String(req.body))


    for item in body["releases"]
        id              = item["basic_information"]["artists"][1]["id"]
        artist          = item["basic_information"]["artists"][1]["name"]
        released        = item["basic_information"]["year"]
        title           = item["basic_information"]["title"]
        year            = ""

        push!(releases, Dict("id" => id,
                            "artist" => artist,
                            "released" => released,
                            "title" => title,
                            "year" => year))
    end

    for release in releases
        local url = string("https://api.discogs.com/artists/", release["id"], "/releases")
        local req = delayedRequest(url, 1)
        

        if req.status == 200
            local body = JSON.parse(String(req.body))

            for item in body["releases"]
                if item["title"] == release["title"]
                    release["year"] = item["year"]
                end
            end
        else
            release["year"] = release["released"]
        end
        #foreach(item -> (item["title"] == release["title"] && release["year"] = item["year"]), body["releases"])
    end

    global data = DataFrames.DataFrame(artist = [], year = [], title = [], id = [], released = [])
    foreach(item -> push!(releases, item), releases)
    CSV.write(joinpath(path, "releases.csv"), data)

    println(string("[ file ] ", joinpath(path, "releases.csv")))
else
    global data = DataFrames.DataFrame(CSV.File(joinpath(path, "releases.csv")))
end

#
sort!(data, cols = [:artist, :year])

begin # Fix and format data
    #local id = 0

    for item in eachrow(data)
        m = match(r"\(.\)", item.artist)
        if ~isnothing(m)
            item.artist = strip(replace(artist, m.match => ""))
        end

        item.artist = replace(artist, "&" => "\\&")
        item.title = replace(title, "&" => "\\&")
    end
end
