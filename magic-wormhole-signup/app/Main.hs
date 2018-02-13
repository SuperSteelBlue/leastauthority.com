{-# LANGUAGE OverloadedStrings #-}

module Main where

import Data.ByteString.Char8 (
  pack
  )

import System.Environment (
  getArgs
  )

import Converge (
  showSubscriptions
  )

main :: IO ()
main = do
  args <- getArgs
  case args of
    manager_url:[] -> showSubscriptions
    otherwise      -> putStrLn "Usage: schmoo <manager url>"
