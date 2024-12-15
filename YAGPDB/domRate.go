{{/*Uses regex trigger "\A(?:\-|<@!?204255221017214977>)\s*(?:domrate|subrate)(?: +|\z)"*/}}

{{/*Unicornia Purple*/}}
{{$color := 5778572}}
{{$serverAvatar := print "https://cdn.discordapp.com/icons/" .Guild.ID "/" .Guild.Icon ".png?size=1024"}}

{{/*Some emoji for displaying result embeds*/}}
{{$domEmoji := "https://cdn.discordapp.com/emojis/695147901407592499.webp?size=128&quality=lossless"}}
{{$subEmoji := "https://cdn.discordapp.com/emojis/729249758715183144.webp?size=128&quality=lossless"}}
{{$superSubEmoji := "https://cdn.discordapp.com/emojis/824660139234820106.webp?size=128&quality=lossless"}}
{{$mysteryEmoji := "https://cdn.discordapp.com/emojis/828672418318778398.gif?size=128&quality=lossless"}}
{{$badGirlEmoji := "https://cdn.discordapp.com/emojis/988245911564058686.webp?size=128&quality=lossless"}}

{{$subRoles := sdict
	"686097362107498504" 1.00
	"768103786119823380" 0.50
	"694788843207131246" 0.50
	"694788849020305451" 0.75
	"694788851155337236" 0.10
	"694788853419999352" 0.05
	"694788854942531607" 0.05
	"1074675006006644736" 0.05
	"696082750775492688" 0.15
	"694790765460848701" 1.00
	"696048918248554627" 1.00
	"708022873058574396" 0.25
	"686098506834116620" 0.05
	"686098381214711837" 1.00
}}

{{$domRoles := sdict
	"686097057190379537" 1.00
	"686097106083119115" 1.00
	"694788857371033640" 1.00
	"694788859015462923" 0.25
	"694788860760031243" 0.25
	"694789801353805862" 0.25
	"694789803153162290" 0.25
	"694790101095546890" 0.25
	"694790104044142612" 1.00
	"694790108230189087" 0.25
	"686098541831127048" 0.10
	"811471307106942996" 0.50
	"1088587344417931407" 1.00
}}

{{/*Get user from argument or user who triggered command*/}}
{{$user := .User}}
{{$args := parseArgs 0 "" (carg "user" "target user")}}
{{if $args.IsSet 0}}
    {{$user = userArg ($args.Get 0)}}
{{end}}

{{/*Get Member object from User ID/Mention*/}}
{{$member := (getMember $user)}}
{{/*Get Member.Nick if it's not nil, otherwise get the User.Username*/}}
{{$name := or $member.Nick $user.Username}}

{{/*Total values of roles for normalization*/}}
{{$domTotal := 0.0}}
{{$subTotal := 0.0}}
{{/*Baseline rating of 0.0*/}}
{{$domRating := 0.0}}
{{$subRating := 0.0}}

{{/*Add points for Dominant Roles*/}}
{{range $k, $v := $domRoles}}
	{{$domTotal = add $domTotal $v}}
	{{if targetHasRoleID $user (toInt $k)}}
		{{$domRating = add $domRating $v}}
	{{end}}
{{end}}
{{/*Normalize dominant rating value*/}}
{{/*$domRating = div $domRating $domTotal*/}}

{{/*Add points for Submissive Roles*/}}
{{range $k, $v := $subRoles}}
	{{$subTotal = add $subTotal $v}}
	{{if targetHasRoleID $user (toInt $k)}}
		{{$subRating = add $subRating $v}}
	{{end}}
{{end}}

{{/*Normalize submissive rating value*/}}
{{/*Disabled because larger % is funnier*/}}
{{/*$subRating = div $subRating $subTotal*/}}

{{/*Calculate final rating and multiply by 100 go get a %*/}}
{{$rating := sub $domRating $subRating}}

{{/*Default Title and Description*/}}
{{$title := "❯ Dom/Sub Rate"}}
{{$description := "Calculating dominance..."}}
{{$thumbnail := (sdict "url" $serverAvatar)}}
{{$footer := "Results scientifically calculated based on member roles."}}

{{/*
If you're rating is above 0, then you're "Dominant".
If it's below 0, then you're "Submissive" and we invert the rating value.
If it's exactly 0, then you're "Mysterious" and we set the rating to 1000%
*/}}

{{/*Set the description and thumbnail based on rating*/}}
{{/*Lilith_btw (She/Her)#3379*/}}
{{if eq $user.ID 155000754816417793}}
	{{/*$title = "❯ Supremely Submissive"*/}}
	{{/*$description = (printf "❯ %s is the Subbiest of Submissives." $name)*/}}
	{{/*$thumbnail = (sdict "url" $superSubEmoji)*/}}
	{{$title = "❯ Just Naughty"}}
	{{$description = (printf "❯ %s is very bad, naughty girl." $name)}}
	{{$thumbnail = (sdict "url" $badGirlEmoji)}}
{{else if gt $rating 0.0}}
	{{$title = "❯ Dominant"}}
	{{$rating = mult $rating 100}}
	{{$description = printf "❯ %s is %.0f%% Dominant." $name $rating}}
	{{$thumbnail = (sdict "url" $domEmoji)}}
{{else if lt $rating 0.0}}
	{{$title = "❯ Submissive"}}
	{{$rating = mult $rating -100}}
	{{$description = printf "❯ %s is %.0f%% Submissive." $name $rating}}
	{{$thumbnail = (sdict "url" $subEmoji)}}
{{else}}
	{{$title = "❯ ???"}}
	{{$description = printf "❯ %s is 1000%% mysterious..." $name}}
	{{$thumbnail = (sdict "url" $mysteryEmoji)}}
{{end}}

{{/*Send the embed*/}}
{{ $embed := cembed
    "title" $title
    "color" $color
    "description" $description
    "thumbnail" $thumbnail
	"footer" (sdict "text" $footer "icon_url" $serverAvatar)
}}

{{sendMessage nil $embed}}

{{/*
    "fields" (cslice 
        (sdict "name" "Dominant" "value" (printf "You are %.0f%% Dominant." (mult $domRating 100)) "inline" false)
        (sdict "name" "Submissive" "value" (printf "You are %.0f%% Submissive." (mult $subRating 100)) "inline" false)
    )
*/}}