from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import CRUD
import create_database
app = Flask(__name__)