# Makefile for source rpm: virt-manager
# $Id$
NAME := virt-manager
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
