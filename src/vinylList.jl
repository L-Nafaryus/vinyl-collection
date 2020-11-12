module vinylList
    import HTTP, JSON
    
    user = "L-Nafaryus"
    fcount = 300
    fsort = "artist"
    req = HTTP.request("GET", string("https://api.discogs.com/users/", user, "/collection/folders/0/releases?per_page=", fcount, "&sort=", fsort))
    items = JSON.parse(String(req.body))
    
    #
    list = String[]

    for item in items["releases"]
        artist  = item["basic_information"]["artists"][1]["name"]
        year    = item["basic_information"]["year"]
        title   = item["basic_information"]["title"]
            
        #
        m = match(r"\(.\)", artist)
        if ~isnothing(m)
            artist = strip(replace(artist, m.match => ""))
        end
        
        artist = replace(artist, "&" => "\\&")
        title = replace(title, "&" => "\\&")
        
        push!(list, string(artist, " & ", year, " & ", title))
    end
    

    #countline = length(list)
    perpage = 50
    #body = String[]
    sortedlist = sort(list)
    
    for n = 1 : length(sortedlist)
        sortedlist[n] = string(n, " & ", sortedlist[n])
    end
    
    function maketable(list)
        startline = "\\begin{longtable}{p{0.05\\textwidth} p{0.35\\textwidth} p{0.05\\textwidth} p{0.5\\textwidth}}"
        columns = "ID & Artist & Year & Title\\\\"
        hline = "\\hline\\\\"
        endline = "\\end{longtable}"
        body = join(list, "\\\\\n")

        return join([startline, columns, hline, body, endline], "\n")
    end
    
    function extract(arr, count)
        if count >= length(arr)
            return arr, []
        elseif count <= 0
            return [], arr
        else
            return arr[1 : count], arr[count + 1 : end]
        end
    end

    buf = copy(sortedlist)
    tables = String[]
    totable = String[]

    while ~isempty(buf)
        global totable, buf = extract(buf, perpage)
        push!(tables, maketable(totable))
    end

    res = join(tables, "\n\\pagebreak\n")
    #if year == 0; year = "n/a" end
    
    ###
    open("build/list.tex", "w") do io
        #for line in sort(list)
            write(io, res)
        #end
    end
end 
