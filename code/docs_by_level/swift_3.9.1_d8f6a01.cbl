### language: swift
### version: 3.9.1
### audience: professional
### detail: medium
### style: logical
### title: This is a swift representation
### timestamp: 1754174500.114906

@audience(professional)
var environment = "development"
let maximumNumberOfLoginAttempts: Int
// maximumNumberOfLoginAttempts has no value yet.


if environment == "development" {
    maximumNumberOfLoginAttempts = 100
} else {
    maximumNumberOfLoginAttempts = 10
}
---end---
