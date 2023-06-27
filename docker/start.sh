#!/bin/bash

cd /plarin_test && uvicorn main:app --reload || exit
