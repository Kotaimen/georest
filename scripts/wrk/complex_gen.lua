chrset = '0123456789abcdefghijklmnopqrstuvwxyz'


function randchr()
    local i = math.random(#chrset)
    return string.sub(chrset, i, i)
end


function randstr(n)
    local l = {}
    for i=1,n do
        l[i] = randchr()
    end
    return table.concat(l)
end


function randpos(scale, offset)
    return math.random() * scale + offset
end


function rand_point()
    return {
        name = 'foo.' .. randstr(6),
        lon = randpos(360, -180.0),
        lat = randpos(180, -90.0),
    }
end


Points = {points = {}, get_i = 1, set_i = 1, max_i = 1000}


function Points:new_point()
    -- create a new point
    if self.set_i > self.max_i then
        self.set_i = 1
    end
    local p = rand_point()
    self.points[self.set_i] = p
    self.set_i = self.set_i + 1
    return p
end


function Points:get_point()
    -- get an old point
    if (self.get_i > self.max_i) or (self.get_i > #self.points) then
        self.get_i = 1
    end
    local p = self.points[self.get_i]
    self.get_i = self.get_i + 1
    return p
end


feature_pattern = [[{
    "type": "Feature",
    "properties": {"f": "b", "u": "t"},
    "geometry": {
        "type": "Point",
        "coordinates": [%s, %s]
    }
}]]


function Points:make_put_feature()
    -- provide a point geometry with some properties
    local point = self:new_point()
    local url = '/features/' .. point.name
    local data = string.format(feature_pattern, point.lon, point.lat)
    local headers = {}
    headers['Content-Type'] = 'application/json'
    headers['Host'] = wrk.headers['Host']
    return wrk.format('PUT', url, headers, data)
end


function Points:make_put_geometry()
    -- provide a point
    local point = self:new_point()
    local url = '/features/' .. point.name .. '/geometry'
    local data = string.format('{"type":"Point","coordinates":[%s,%s]}',
                               point.lon, point.lat)
    local headers = {}
    headers['Content-Type'] = 'application/json'
    headers['Host'] = wrk.headers['Host']
    return wrk.format('PUT', url, headers, data)
end


binary_op_list = {'distance', 'equals', 'symmetric_difference'}


function Points:make_binary_ops()
    local point1 = self:get_point()
    local point2 = self:get_point()
    local op = binary_op_list[math.random(#binary_op_list)]
    local url = '/operations/' .. op .. '/' .. point1.name .. '/' .. point2.name
    return wrk.format('GET', url)
end


function magicseed()
    local f = io.popen('xxd -l 4 -p /dev/urandom') -- use /dev/random if no uran
    local randhex = f:read()
    f:close()
    return loadstring('return 0x' .. randhex)()
end


gen = coroutine.create(function()
    -- put some geometries at first
    for i = 1, 50 do
        coroutine.yield(Points:make_put_geometry())
    end
    while true do
        local dice = math.random(100)

        if dice <= 30 then
            -- 30% geometry
            coroutine.yield(Points:make_put_geometry())
        elseif dice <= 60 then
            -- 30% feature
            coroutine.yield(Points:make_put_feature())
        else
            -- 40% op
            coroutine.yield(Points:make_binary_ops())
        end
    end
end)


function init(args)
    wrk.init(args)
    math.randomseed(magicseed())
end


function request()
    local _, req = coroutine.resume(gen)
    return req
end

