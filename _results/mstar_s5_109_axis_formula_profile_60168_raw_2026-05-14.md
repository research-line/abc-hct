# S5 p=2 109-Axis Formula Profile

## Summary

- input: `_results\mstar_s5_109_axis_transition_profile_60168_raw_2026-05-14.json`
- transition records: `2304`
- fields: `9`

## Field Overview

| field | count | exact identities | source-v linear rules | image-v linear rules |
|---|---:|---|---:|---:|
| `base-gcd-v-line:TT:1:exact` | 192 | gcd(image_u,N)=gcd(target_u,N), gcd(image_v,N)=gcd(target_v,N), image=target, image_u=target_u, source_u=g | 1 | 16 |
| `base-gcd-v-line:TT:1:same-u` | 192 | gcd(image_u,N)=gcd(target_u,N), gcd(image_v,N)=gcd(target_v,N), image_u=target_u, source_u=g | 1 | 3 |
| `base-gcd-v-line:id:-1:other` | 384 | source_u=g | 3 | 3 |
| `even-intermediate:T:-1:other` | 384 | source_u even non-109 | 1 | 3 |
| `even-intermediate:T:1:exact` | 192 | gcd(image_u,N)=gcd(target_u,N), gcd(image_v,N)=gcd(target_v,N), image=target, image_u=target_u, source_u even non-109 | 3 | 16 |
| `even-intermediate:T:1:same-u` | 192 | gcd(image_u,N)=gcd(target_u,N), gcd(image_v,N)=gcd(target_v,N), image_u=target_u, source_u even non-109 | 3 | 3 |
| `target-109d-axis:TT:-1:other` | 384 | source_u=109*d | 1 | 3 |
| `target-109d-axis:id:1:exact` | 192 | gcd(image_u,N)=gcd(target_u,N), gcd(image_v,N)=gcd(target_v,N), image=target, image_u=target_u, source_u=109*d | 16 | 16 |
| `target-109d-axis:id:1:same-u` | 192 | gcd(image_u,N)=gcd(target_u,N), gcd(image_v,N)=gcd(target_v,N), image_u=target_u, source_u=109*d | 3 | 3 |

## `base-gcd-v-line:TT:1:exact`

- count: `192`
- exact identities: `{'gcd(image_u,N)=gcd(target_u,N)': 192, 'gcd(image_v,N)=gcd(target_v,N)': 192, 'image=target': 192, 'image_u=target_u': 192, 'source_u=g': 192}`
- quotient v-relations: `{'image_v=target_v mod N/u': 192}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 88}, {'key': '3,1', 'count': 44}, {'key': '1,3', 'count': 44}, {'key': '23,1', 'count': 4}, {'key': '1,23', 'count': 4}, {'key': '69,1', 'count': 2}, {'key': '23,3', 'count': 2}, {'key': '3,23', 'count': 2}, {'key': '1,69', 'count': 2}]`
- source-u expression distribution: `[{'key': 'g', 'count': 192}]`
- source-v minus target-v mod 109: `[{'key': '97', 'count': 6}, {'key': '103', 'count': 6}, {'key': '91', 'count': 5}, {'key': '63', 'count': 5}, {'key': '51', 'count': 4}, {'key': '101', 'count': 4}, {'key': '1', 'count': 4}, {'key': '67', 'count': 4}, {'key': '62', 'count': 4}, {'key': '55', 'count': 4}, {'key': '61', 'count': 4}, {'key': '107', 'count': 4}, {'key': '53', 'count': 3}, {'key': '98', 'count': 3}, {'key': '83', 'count': 3}, {'key': '21', 'count': 3}, {'key': '95', 'count': 3}, {'key': '13', 'count': 3}, {'key': '7', 'count': 3}, {'key': '32', 'count': 3}]`
- source-v plus target-v mod 109: `[{'key': '0', 'count': 9}, {'key': '12', 'count': 7}, {'key': '10', 'count': 6}, {'key': '4', 'count': 5}, {'key': '16', 'count': 4}, {'key': '6', 'count': 4}, {'key': '40', 'count': 4}, {'key': '45', 'count': 4}, {'key': '52', 'count': 4}, {'key': '46', 'count': 4}, {'key': '24', 'count': 3}, {'key': '101', 'count': 3}, {'key': '106', 'count': 3}, {'key': '41', 'count': 3}, {'key': '35', 'count': 3}, {'key': '94', 'count': 3}, {'key': '100', 'count': 3}, {'key': '71', 'count': 3}, {'key': '78', 'count': 3}, {'key': '21', 'count': 3}]`
- image-v minus target-v mod 109: `[{'key': '0', 'count': 192}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 0}, {'a': 1, 'b': 1}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 3, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 4, 'examples': [{'a': 1, 'b': 0}, {'a': 3, 'b': 2}], 'count': 2}, {'modulus': 8, 'examples': [{'a': 1, 'b': 0}, {'a': 5, 'b': 4}], 'count': 2}, {'modulus': 23, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 46, 'examples': [{'a': 1, 'b': 0}, {'a': 24, 'b': 23}], 'count': 2}, {'modulus': 69, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 92, 'examples': [{'a': 1, 'b': 0}, {'a': 47, 'b': 46}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '108', 'count': 138}, {'key': '106', 'count': 46}, {'key': '86', 'count': 6}, {'key': '40', 'count': 2}]`
- per-target image-v mod109 signatures: `[{'key': '11', 'count': 6}, {'key': '7', 'count': 5}, {'key': '1', 'count': 5}, {'key': '107', 'count': 4}, {'key': '5', 'count': 4}, {'key': '41', 'count': 4}]`

## `base-gcd-v-line:TT:1:same-u`

- count: `192`
- exact identities: `{'gcd(image_u,N)=gcd(target_u,N)': 192, 'gcd(image_v,N)=gcd(target_v,N)': 192, 'image_u=target_u': 192, 'source_u=g': 192}`
- quotient v-relations: `{'image_v=-target_v mod N/u': 192}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 88}, {'key': '3,1', 'count': 44}, {'key': '1,3', 'count': 44}, {'key': '23,1', 'count': 4}, {'key': '1,23', 'count': 4}, {'key': '69,1', 'count': 2}, {'key': '23,3', 'count': 2}, {'key': '3,23', 'count': 2}, {'key': '1,69', 'count': 2}]`
- source-u expression distribution: `[{'key': 'g', 'count': 192}]`
- source-v minus target-v mod 109: `[{'key': '103', 'count': 6}, {'key': '97', 'count': 6}, {'key': '91', 'count': 5}, {'key': '63', 'count': 5}, {'key': '107', 'count': 4}, {'key': '61', 'count': 4}, {'key': '67', 'count': 4}, {'key': '62', 'count': 4}, {'key': '55', 'count': 4}, {'key': '101', 'count': 4}, {'key': '1', 'count': 4}, {'key': '51', 'count': 4}, {'key': '105', 'count': 3}, {'key': '29', 'count': 3}, {'key': '23', 'count': 3}, {'key': '21', 'count': 3}, {'key': '7', 'count': 3}, {'key': '92', 'count': 3}, {'key': '86', 'count': 3}, {'key': '35', 'count': 3}]`
- source-v plus target-v mod 109: `[{'key': '0', 'count': 9}, {'key': '12', 'count': 7}, {'key': '10', 'count': 6}, {'key': '4', 'count': 5}, {'key': '46', 'count': 4}, {'key': '40', 'count': 4}, {'key': '45', 'count': 4}, {'key': '52', 'count': 4}, {'key': '16', 'count': 4}, {'key': '6', 'count': 4}, {'key': '78', 'count': 3}, {'key': '32', 'count': 3}, {'key': '84', 'count': 3}, {'key': '64', 'count': 3}, {'key': '100', 'count': 3}, {'key': '15', 'count': 3}, {'key': '21', 'count': 3}, {'key': '71', 'count': 3}, {'key': '94', 'count': 3}, {'key': '35', 'count': 3}]`
- image-v minus target-v mod 109: `[{'key': '55', 'count': 4}, {'key': '10', 'count': 4}, {'key': '6', 'count': 4}, {'key': '0', 'count': 4}, {'key': '103', 'count': 4}, {'key': '18', 'count': 4}, {'key': '5', 'count': 3}, {'key': '1', 'count': 3}, {'key': '67', 'count': 3}, {'key': '50', 'count': 3}, {'key': '46', 'count': 3}, {'key': '105', 'count': 3}, {'key': '79', 'count': 3}, {'key': '34', 'count': 3}, {'key': '41', 'count': 3}, {'key': '90', 'count': 3}, {'key': '106', 'count': 3}, {'key': '78', 'count': 3}, {'key': '27', 'count': 3}, {'key': '14', 'count': 3}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 0}, {'a': 1, 'b': 1}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 4, 'examples': [{'a': 1, 'b': 2}, {'a': 3, 'b': 0}], 'count': 2}, {'modulus': 8, 'examples': [{'a': 3, 'b': 4}, {'a': 7, 'b': 0}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '108', 'count': 138}, {'key': '106', 'count': 46}, {'key': '86', 'count': 6}, {'key': '40', 'count': 2}]`
- per-target image-v mod109 signatures: `[{'key': '4', 'count': 4}, {'key': '83', 'count': 4}, {'key': '31', 'count': 4}, {'key': '29', 'count': 4}, {'key': '71', 'count': 4}, {'key': '34', 'count': 4}]`

## `base-gcd-v-line:id:-1:other`

- count: `384`
- exact identities: `{'source_u=g': 384}`
- quotient v-relations: `{'image_v=-target_v mod N/u': 6, 'image_v=target_v mod N/u': 6, 'source_v=-target_v mod N/u': 6, 'source_v=target_v mod N/u': 6}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 176}, {'key': '3,1', 'count': 88}, {'key': '1,3', 'count': 88}, {'key': '23,1', 'count': 8}, {'key': '1,23', 'count': 8}, {'key': '69,1', 'count': 4}, {'key': '23,3', 'count': 4}, {'key': '3,23', 'count': 4}, {'key': '1,69', 'count': 4}]`
- source-u expression distribution: `[{'key': 'g', 'count': 384}]`
- source-v minus target-v mod 109: `[{'key': '98', 'count': 12}, {'key': '108', 'count': 10}, {'key': '102', 'count': 10}, {'key': '106', 'count': 8}, {'key': '24', 'count': 8}, {'key': '62', 'count': 8}, {'key': '68', 'count': 8}, {'key': '56', 'count': 8}, {'key': '104', 'count': 8}, {'key': '2', 'count': 8}, {'key': '30', 'count': 6}, {'key': '76', 'count': 6}, {'key': '63', 'count': 6}, {'key': '49', 'count': 6}, {'key': '93', 'count': 6}, {'key': '87', 'count': 6}, {'key': '92', 'count': 6}, {'key': '96', 'count': 6}, {'key': '14', 'count': 6}, {'key': '73', 'count': 6}]`
- source-v plus target-v mod 109: `[{'key': '11', 'count': 12}, {'key': '1', 'count': 10}, {'key': '7', 'count': 10}, {'key': '3', 'count': 8}, {'key': '85', 'count': 8}, {'key': '47', 'count': 8}, {'key': '41', 'count': 8}, {'key': '53', 'count': 8}, {'key': '5', 'count': 8}, {'key': '107', 'count': 8}, {'key': '79', 'count': 6}, {'key': '33', 'count': 6}, {'key': '46', 'count': 6}, {'key': '60', 'count': 6}, {'key': '16', 'count': 6}, {'key': '22', 'count': 6}, {'key': '17', 'count': 6}, {'key': '13', 'count': 6}, {'key': '95', 'count': 6}, {'key': '36', 'count': 6}]`
- image-v minus target-v mod 109: `[{'key': '98', 'count': 12}, {'key': '108', 'count': 10}, {'key': '102', 'count': 10}, {'key': '106', 'count': 8}, {'key': '24', 'count': 8}, {'key': '62', 'count': 8}, {'key': '68', 'count': 8}, {'key': '56', 'count': 8}, {'key': '104', 'count': 8}, {'key': '2', 'count': 8}, {'key': '30', 'count': 6}, {'key': '76', 'count': 6}, {'key': '63', 'count': 6}, {'key': '49', 'count': 6}, {'key': '93', 'count': 6}, {'key': '87', 'count': 6}, {'key': '92', 'count': 6}, {'key': '96', 'count': 6}, {'key': '14', 'count': 6}, {'key': '73', 'count': 6}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 109, 'examples': [{'a': 0, 'b': 0}], 'count': 1}, {'modulus': 218, 'examples': [{'a': 0, 'b': 109}, {'a': 109, 'b': 0}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 109, 'examples': [{'a': 0, 'b': 0}], 'count': 1}, {'modulus': 218, 'examples': [{'a': 0, 'b': 109}, {'a': 109, 'b': 0}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '0|0', 'count': 192}]`
- per-target image-v mod109 signatures: `[{'key': '0|0', 'count': 192}]`

## `even-intermediate:T:-1:other`

- count: `384`
- exact identities: `{'source_u even non-109': 384}`
- quotient v-relations: `{'image_v=-target_v mod N/u': 6, 'image_v=target_v mod N/u': 6, 'source_v=-target_v mod N/u': 14, 'source_v=target_v mod N/u': 13}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 176}, {'key': '3,1', 'count': 88}, {'key': '1,3', 'count': 88}, {'key': '1,23', 'count': 8}, {'key': '23,1', 'count': 8}, {'key': '3,23', 'count': 4}, {'key': '23,3', 'count': 4}, {'key': '69,1', 'count': 4}, {'key': '1,69', 'count': 4}]`
- source-u expression distribution: `[{'key': 'even_non109', 'count': 384}]`
- source-v minus target-v mod 109: `[{'key': '96', 'count': 12}, {'key': '100', 'count': 12}, {'key': '98', 'count': 11}, {'key': '50', 'count': 10}, {'key': '52', 'count': 10}, {'key': '0', 'count': 9}, {'key': '74', 'count': 8}, {'key': '102', 'count': 8}, {'key': '15', 'count': 7}, {'key': '2', 'count': 7}, {'key': '65', 'count': 7}, {'key': '106', 'count': 6}, {'key': '72', 'count': 6}, {'key': '94', 'count': 6}, {'key': '4', 'count': 6}, {'key': '87', 'count': 6}, {'key': '28', 'count': 6}, {'key': '48', 'count': 6}, {'key': '85', 'count': 5}, {'key': '22', 'count': 5}]`
- source-v plus target-v mod 109: `[{'key': '9', 'count': 12}, {'key': '108', 'count': 10}, {'key': '33', 'count': 9}, {'key': '83', 'count': 9}, {'key': '7', 'count': 9}, {'key': '11', 'count': 8}, {'key': '70', 'count': 8}, {'key': '35', 'count': 8}, {'key': '0', 'count': 8}, {'key': '45', 'count': 7}, {'key': '105', 'count': 6}, {'key': '58', 'count': 6}, {'key': '31', 'count': 6}, {'key': '46', 'count': 6}, {'key': '34', 'count': 6}, {'key': '1', 'count': 6}, {'key': '94', 'count': 6}, {'key': '81', 'count': 6}, {'key': '75', 'count': 6}, {'key': '96', 'count': 6}]`
- image-v minus target-v mod 109: `[{'key': '98', 'count': 12}, {'key': '108', 'count': 10}, {'key': '102', 'count': 10}, {'key': '2', 'count': 8}, {'key': '62', 'count': 8}, {'key': '24', 'count': 8}, {'key': '68', 'count': 8}, {'key': '106', 'count': 8}, {'key': '104', 'count': 8}, {'key': '56', 'count': 8}, {'key': '74', 'count': 6}, {'key': '49', 'count': 6}, {'key': '94', 'count': 6}, {'key': '87', 'count': 6}, {'key': '76', 'count': 6}, {'key': '7', 'count': 6}, {'key': '86', 'count': 6}, {'key': '96', 'count': 6}, {'key': '92', 'count': 6}, {'key': '63', 'count': 6}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 109, 'examples': [{'a': 0, 'b': 0}], 'count': 1}, {'modulus': 218, 'examples': [{'a': 0, 'b': 109}, {'a': 109, 'b': 0}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '105|107', 'count': 44}, {'key': '101|107', 'count': 44}, {'key': '107|85', 'count': 22}, {'key': '107|97', 'count': 22}, {'key': '103|105', 'count': 22}, {'key': '101|103', 'count': 22}]`
- per-target image-v mod109 signatures: `[{'key': '0|0', 'count': 192}]`

## `even-intermediate:T:1:exact`

- count: `192`
- exact identities: `{'gcd(image_u,N)=gcd(target_u,N)': 192, 'gcd(image_v,N)=gcd(target_v,N)': 192, 'image=target': 192, 'image_u=target_u': 192, 'source_u even non-109': 192}`
- quotient v-relations: `{'image_v=target_v mod N/u': 192, 'source_v=-target_v mod N/u': 1, 'source_v=target_v mod N/u': 2}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 88}, {'key': '1,3', 'count': 44}, {'key': '3,1', 'count': 44}, {'key': '23,1', 'count': 4}, {'key': '1,23', 'count': 4}, {'key': '1,69', 'count': 2}, {'key': '23,3', 'count': 2}, {'key': '3,23', 'count': 2}, {'key': '69,1', 'count': 2}]`
- source-u expression distribution: `[{'key': 'even_non109', 'count': 192}]`
- source-v minus target-v mod 109: `[{'key': '98', 'count': 6}, {'key': '108', 'count': 5}, {'key': '102', 'count': 5}, {'key': '68', 'count': 4}, {'key': '106', 'count': 4}, {'key': '2', 'count': 4}, {'key': '62', 'count': 4}, {'key': '24', 'count': 4}, {'key': '56', 'count': 4}, {'key': '104', 'count': 4}, {'key': '54', 'count': 3}, {'key': '14', 'count': 3}, {'key': '63', 'count': 3}, {'key': '7', 'count': 3}, {'key': '30', 'count': 3}, {'key': '96', 'count': 3}, {'key': '73', 'count': 3}, {'key': '86', 'count': 3}, {'key': '49', 'count': 3}, {'key': '87', 'count': 3}]`
- source-v plus target-v mod 109: `[{'key': '11', 'count': 6}, {'key': '1', 'count': 5}, {'key': '7', 'count': 5}, {'key': '41', 'count': 4}, {'key': '3', 'count': 4}, {'key': '107', 'count': 4}, {'key': '47', 'count': 4}, {'key': '85', 'count': 4}, {'key': '53', 'count': 4}, {'key': '5', 'count': 4}, {'key': '55', 'count': 3}, {'key': '95', 'count': 3}, {'key': '46', 'count': 3}, {'key': '102', 'count': 3}, {'key': '79', 'count': 3}, {'key': '13', 'count': 3}, {'key': '36', 'count': 3}, {'key': '23', 'count': 3}, {'key': '60', 'count': 3}, {'key': '22', 'count': 3}]`
- image-v minus target-v mod 109: `[{'key': '0', 'count': 192}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 109, 'examples': [{'a': 0, 'b': 0}], 'count': 1}, {'modulus': 218, 'examples': [{'a': 0, 'b': 109}, {'a': 109, 'b': 0}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 3, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 4, 'examples': [{'a': 1, 'b': 0}, {'a': 3, 'b': 2}], 'count': 2}, {'modulus': 8, 'examples': [{'a': 1, 'b': 0}, {'a': 5, 'b': 4}], 'count': 2}, {'modulus': 23, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 46, 'examples': [{'a': 1, 'b': 0}, {'a': 24, 'b': 23}], 'count': 2}, {'modulus': 69, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 92, 'examples': [{'a': 1, 'b': 0}, {'a': 47, 'b': 46}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '0', 'count': 192}]`
- per-target image-v mod109 signatures: `[{'key': '11', 'count': 6}, {'key': '1', 'count': 5}, {'key': '7', 'count': 5}, {'key': '41', 'count': 4}, {'key': '3', 'count': 4}, {'key': '107', 'count': 4}]`

## `even-intermediate:T:1:same-u`

- count: `192`
- exact identities: `{'gcd(image_u,N)=gcd(target_u,N)': 192, 'gcd(image_v,N)=gcd(target_v,N)': 192, 'image_u=target_u': 192, 'source_u even non-109': 192}`
- quotient v-relations: `{'image_v=-target_v mod N/u': 192, 'source_v=-target_v mod N/u': 2, 'source_v=target_v mod N/u': 6}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 88}, {'key': '1,3', 'count': 44}, {'key': '3,1', 'count': 44}, {'key': '1,23', 'count': 4}, {'key': '23,1', 'count': 4}, {'key': '69,1', 'count': 2}, {'key': '3,23', 'count': 2}, {'key': '23,3', 'count': 2}, {'key': '1,69', 'count': 2}]`
- source-u expression distribution: `[{'key': 'even_non109', 'count': 192}]`
- source-v minus target-v mod 109: `[{'key': '98', 'count': 6}, {'key': '102', 'count': 5}, {'key': '108', 'count': 5}, {'key': '68', 'count': 4}, {'key': '24', 'count': 4}, {'key': '62', 'count': 4}, {'key': '2', 'count': 4}, {'key': '106', 'count': 4}, {'key': '56', 'count': 4}, {'key': '104', 'count': 4}, {'key': '73', 'count': 3}, {'key': '76', 'count': 3}, {'key': '74', 'count': 3}, {'key': '86', 'count': 3}, {'key': '84', 'count': 3}, {'key': '49', 'count': 3}, {'key': '93', 'count': 3}, {'key': '30', 'count': 3}, {'key': '14', 'count': 3}, {'key': '87', 'count': 3}]`
- source-v plus target-v mod 109: `[{'key': '11', 'count': 6}, {'key': '7', 'count': 5}, {'key': '1', 'count': 5}, {'key': '41', 'count': 4}, {'key': '85', 'count': 4}, {'key': '47', 'count': 4}, {'key': '107', 'count': 4}, {'key': '3', 'count': 4}, {'key': '53', 'count': 4}, {'key': '5', 'count': 4}, {'key': '36', 'count': 3}, {'key': '33', 'count': 3}, {'key': '35', 'count': 3}, {'key': '23', 'count': 3}, {'key': '25', 'count': 3}, {'key': '60', 'count': 3}, {'key': '16', 'count': 3}, {'key': '79', 'count': 3}, {'key': '95', 'count': 3}, {'key': '22', 'count': 3}]`
- image-v minus target-v mod 109: `[{'key': '55', 'count': 4}, {'key': '103', 'count': 4}, {'key': '0', 'count': 4}, {'key': '6', 'count': 4}, {'key': '18', 'count': 4}, {'key': '10', 'count': 4}, {'key': '78', 'count': 3}, {'key': '14', 'count': 3}, {'key': '50', 'count': 3}, {'key': '27', 'count': 3}, {'key': '46', 'count': 3}, {'key': '66', 'count': 3}, {'key': '21', 'count': 3}, {'key': '105', 'count': 3}, {'key': '67', 'count': 3}, {'key': '1', 'count': 3}, {'key': '44', 'count': 3}, {'key': '106', 'count': 3}, {'key': '41', 'count': 3}, {'key': '40', 'count': 3}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 109, 'examples': [{'a': 0, 'b': 0}], 'count': 1}, {'modulus': 218, 'examples': [{'a': 0, 'b': 109}, {'a': 109, 'b': 0}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 4, 'examples': [{'a': 1, 'b': 2}, {'a': 3, 'b': 0}], 'count': 2}, {'modulus': 8, 'examples': [{'a': 3, 'b': 4}, {'a': 7, 'b': 0}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '0', 'count': 192}]`
- per-target image-v mod109 signatures: `[{'key': '34', 'count': 4}, {'key': '83', 'count': 4}, {'key': '31', 'count': 4}, {'key': '29', 'count': 4}, {'key': '71', 'count': 4}, {'key': '4', 'count': 4}]`

## `target-109d-axis:TT:-1:other`

- count: `384`
- exact identities: `{'source_u=109*d': 384}`
- quotient v-relations: `{'image_v=-target_v mod N/u': 6, 'image_v=target_v mod N/u': 6}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 176}, {'key': '1,3', 'count': 88}, {'key': '3,1', 'count': 88}, {'key': '1,23', 'count': 8}, {'key': '23,1', 'count': 8}, {'key': '1,69', 'count': 4}, {'key': '3,23', 'count': 4}, {'key': '23,3', 'count': 4}, {'key': '69,1', 'count': 4}]`
- source-u expression distribution: `[{'key': '109*d', 'count': 384}]`
- source-v minus target-v mod 109: `[{'key': '0', 'count': 113}, {'key': '7', 'count': 46}, {'key': '41', 'count': 18}, {'key': '75', 'count': 18}, {'key': '13', 'count': 7}, {'key': '100', 'count': 4}, {'key': '1', 'count': 3}, {'key': '21', 'count': 3}, {'key': '105', 'count': 3}, {'key': '24', 'count': 3}, {'key': '44', 'count': 3}, {'key': '52', 'count': 3}, {'key': '84', 'count': 3}, {'key': '27', 'count': 3}, {'key': '35', 'count': 3}, {'key': '55', 'count': 3}, {'key': '6', 'count': 3}, {'key': '14', 'count': 3}, {'key': '22', 'count': 3}, {'key': '94', 'count': 3}]`
- source-v plus target-v mod 109: `[{'key': '7', 'count': 142}, {'key': '14', 'count': 29}, {'key': '48', 'count': 13}, {'key': '13', 'count': 8}, {'key': '41', 'count': 7}, {'key': '61', 'count': 4}, {'key': '15', 'count': 4}, {'key': '9', 'count': 4}, {'key': '37', 'count': 4}, {'key': '20', 'count': 3}, {'key': '32', 'count': 3}, {'key': '44', 'count': 3}, {'key': '56', 'count': 3}, {'key': '72', 'count': 3}, {'key': '96', 'count': 3}, {'key': '11', 'count': 3}, {'key': '35', 'count': 3}, {'key': '43', 'count': 3}, {'key': '75', 'count': 3}, {'key': '38', 'count': 3}]`
- image-v minus target-v mod 109: `[{'key': '98', 'count': 12}, {'key': '108', 'count': 10}, {'key': '102', 'count': 10}, {'key': '106', 'count': 8}, {'key': '104', 'count': 8}, {'key': '24', 'count': 8}, {'key': '68', 'count': 8}, {'key': '62', 'count': 8}, {'key': '56', 'count': 8}, {'key': '2', 'count': 8}, {'key': '7', 'count': 6}, {'key': '93', 'count': 6}, {'key': '87', 'count': 6}, {'key': '73', 'count': 6}, {'key': '63', 'count': 6}, {'key': '49', 'count': 6}, {'key': '14', 'count': 6}, {'key': '84', 'count': 6}, {'key': '76', 'count': 6}, {'key': '74', 'count': 6}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 0}, {'a': 1, 'b': 1}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 109, 'examples': [{'a': 0, 'b': 0}], 'count': 1}, {'modulus': 218, 'examples': [{'a': 0, 'b': 109}, {'a': 109, 'b': 0}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '7|7', 'count': 3}, {'key': '1|13', 'count': 3}, {'key': '104|19', 'count': 3}, {'key': '25|98', 'count': 3}, {'key': '31|92', 'count': 3}, {'key': '37|86', 'count': 3}]`
- per-target image-v mod109 signatures: `[{'key': '0|0', 'count': 192}]`

## `target-109d-axis:id:1:exact`

- count: `192`
- exact identities: `{'gcd(image_u,N)=gcd(target_u,N)': 192, 'gcd(image_v,N)=gcd(target_v,N)': 192, 'image=target': 192, 'image_u=target_u': 192, 'source_u=109*d': 192}`
- quotient v-relations: `{'image_v=target_v mod N/u': 192, 'source_v=target_v mod N/u': 192}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 88}, {'key': '1,3', 'count': 44}, {'key': '3,1', 'count': 44}, {'key': '1,23', 'count': 4}, {'key': '23,1', 'count': 4}, {'key': '1,69', 'count': 2}, {'key': '3,23', 'count': 2}, {'key': '23,3', 'count': 2}, {'key': '69,1', 'count': 2}]`
- source-u expression distribution: `[{'key': '109*d', 'count': 192}]`
- source-v minus target-v mod 109: `[{'key': '0', 'count': 192}]`
- source-v plus target-v mod 109: `[{'key': '22', 'count': 6}, {'key': '2', 'count': 5}, {'key': '14', 'count': 5}, {'key': '6', 'count': 4}, {'key': '10', 'count': 4}, {'key': '94', 'count': 4}, {'key': '106', 'count': 4}, {'key': '61', 'count': 4}, {'key': '105', 'count': 4}, {'key': '82', 'count': 4}, {'key': '26', 'count': 3}, {'key': '30', 'count': 3}, {'key': '34', 'count': 3}, {'key': '46', 'count': 3}, {'key': '50', 'count': 3}, {'key': '66', 'count': 3}, {'key': '1', 'count': 3}, {'key': '49', 'count': 3}, {'key': '81', 'count': 3}, {'key': '32', 'count': 3}]`
- image-v minus target-v mod 109: `[{'key': '0', 'count': 192}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 3, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 4, 'examples': [{'a': 1, 'b': 0}, {'a': 3, 'b': 2}], 'count': 2}, {'modulus': 8, 'examples': [{'a': 1, 'b': 0}, {'a': 5, 'b': 4}], 'count': 2}, {'modulus': 23, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 46, 'examples': [{'a': 1, 'b': 0}, {'a': 24, 'b': 23}], 'count': 2}, {'modulus': 69, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 92, 'examples': [{'a': 1, 'b': 0}, {'a': 47, 'b': 46}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 3, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 4, 'examples': [{'a': 1, 'b': 0}, {'a': 3, 'b': 2}], 'count': 2}, {'modulus': 8, 'examples': [{'a': 1, 'b': 0}, {'a': 5, 'b': 4}], 'count': 2}, {'modulus': 23, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 46, 'examples': [{'a': 1, 'b': 0}, {'a': 24, 'b': 23}], 'count': 2}, {'modulus': 69, 'examples': [{'a': 1, 'b': 0}], 'count': 1}, {'modulus': 92, 'examples': [{'a': 1, 'b': 0}, {'a': 47, 'b': 46}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '11', 'count': 6}, {'key': '1', 'count': 5}, {'key': '7', 'count': 5}, {'key': '3', 'count': 4}, {'key': '5', 'count': 4}, {'key': '47', 'count': 4}]`
- per-target image-v mod109 signatures: `[{'key': '11', 'count': 6}, {'key': '1', 'count': 5}, {'key': '7', 'count': 5}, {'key': '3', 'count': 4}, {'key': '5', 'count': 4}, {'key': '47', 'count': 4}]`

## `target-109d-axis:id:1:same-u`

- count: `192`
- exact identities: `{'gcd(image_u,N)=gcd(target_u,N)': 192, 'gcd(image_v,N)=gcd(target_v,N)': 192, 'image_u=target_u': 192, 'source_u=109*d': 192}`
- quotient v-relations: `{'image_v=-target_v mod N/u': 192, 'source_v=-target_v mod N/u': 192}`
- target `(d,g)` distribution: `[{'key': '1,1', 'count': 88}, {'key': '1,3', 'count': 44}, {'key': '3,1', 'count': 44}, {'key': '1,23', 'count': 4}, {'key': '23,1', 'count': 4}, {'key': '1,69', 'count': 2}, {'key': '3,23', 'count': 2}, {'key': '23,3', 'count': 2}, {'key': '69,1', 'count': 2}]`
- source-u expression distribution: `[{'key': '109*d', 'count': 192}]`
- source-v minus target-v mod 109: `[{'key': '55', 'count': 4}, {'key': '10', 'count': 4}, {'key': '18', 'count': 4}, {'key': '0', 'count': 4}, {'key': '6', 'count': 4}, {'key': '103', 'count': 4}, {'key': '67', 'count': 3}, {'key': '79', 'count': 3}, {'key': '34', 'count': 3}, {'key': '46', 'count': 3}, {'key': '50', 'count': 3}, {'key': '78', 'count': 3}, {'key': '90', 'count': 3}, {'key': '1', 'count': 3}, {'key': '21', 'count': 3}, {'key': '41', 'count': 3}, {'key': '105', 'count': 3}, {'key': '40', 'count': 3}, {'key': '44', 'count': 3}, {'key': '27', 'count': 3}]`
- source-v plus target-v mod 109: `[{'key': '7', 'count': 136}, {'key': '41', 'count': 30}, {'key': '75', 'count': 15}, {'key': '24', 'count': 5}, {'key': '14', 'count': 3}, {'key': '48', 'count': 1}, {'key': '16', 'count': 1}, {'key': '8', 'count': 1}]`
- image-v minus target-v mod 109: `[{'key': '55', 'count': 4}, {'key': '10', 'count': 4}, {'key': '18', 'count': 4}, {'key': '0', 'count': 4}, {'key': '6', 'count': 4}, {'key': '103', 'count': 4}, {'key': '67', 'count': 3}, {'key': '79', 'count': 3}, {'key': '34', 'count': 3}, {'key': '46', 'count': 3}, {'key': '50', 'count': 3}, {'key': '78', 'count': 3}, {'key': '90', 'count': 3}, {'key': '1', 'count': 3}, {'key': '21', 'count': 3}, {'key': '41', 'count': 3}, {'key': '105', 'count': 3}, {'key': '40', 'count': 3}, {'key': '44', 'count': 3}, {'key': '27', 'count': 3}]`
- source-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 4, 'examples': [{'a': 1, 'b': 2}, {'a': 3, 'b': 0}], 'count': 2}, {'modulus': 8, 'examples': [{'a': 3, 'b': 4}, {'a': 7, 'b': 0}], 'count': 2}]`
- image-v linear rules: `[{'modulus': 2, 'examples': [{'a': 0, 'b': 1}, {'a': 1, 'b': 0}], 'count': 2}, {'modulus': 4, 'examples': [{'a': 1, 'b': 2}, {'a': 3, 'b': 0}], 'count': 2}, {'modulus': 8, 'examples': [{'a': 3, 'b': 4}, {'a': 7, 'b': 0}], 'count': 2}]`
- per-target source-v mod109 signatures: `[{'key': '29', 'count': 4}, {'key': '31', 'count': 4}, {'key': '71', 'count': 4}, {'key': '83', 'count': 4}, {'key': '4', 'count': 4}, {'key': '34', 'count': 4}]`
- per-target image-v mod109 signatures: `[{'key': '29', 'count': 4}, {'key': '31', 'count': 4}, {'key': '71', 'count': 4}, {'key': '83', 'count': 4}, {'key': '4', 'count': 4}, {'key': '34', 'count': 4}]`